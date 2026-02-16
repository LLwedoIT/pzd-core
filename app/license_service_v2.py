"""
Enhanced License Service with Online Validation

Validates license keys against the PZDetector™ license API.
Falls back to cached validation if offline.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import hashlib

try:
    import requests
except ImportError:
    requests = None


class LicenseService:
    """License service with online validation and trial management."""

    def __init__(self, trial_days: int = 7, purchase_url: str = "", api_url: str = "", logger=None):
        self.trial_days = trial_days
        self.purchase_url = purchase_url
        self.api_url = api_url or "https://api.pzdetector.com"
        self.logger = logger
        self.license_path = self._default_license_path()
        self.data = self._load_or_create()
        self.device_id = self._get_device_id()

    def _log(self, level: str, message: str):
        if self.logger:
            log_fn = getattr(self.logger, level, None)
            if log_fn:
                log_fn(message, "LicenseService")
                return
        print(f"[LicenseService] {message}")

    def _default_license_path(self) -> Path:
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        return Path(appdata) / "PZDetector" / "license.json"

    def _get_device_id(self) -> str:
        """Get or create a unique device ID."""
        device_id_file = self.license_path.parent / "device_id"
        
        if device_id_file.exists():
            try:
                return device_id_file.read_text().strip()
            except Exception:
                pass
        
        # Generate new device ID based on hardware
        try:
            import platform
            hardware_info = f"{platform.node()}-{platform.machine()}"
            device_id = hashlib.sha256(hardware_info.encode()).hexdigest()[:16]
        except Exception:
            device_id = str(uuid.uuid4())[:16]
        
        try:
            device_id_file.parent.mkdir(parents=True, exist_ok=True)
            device_id_file.write_text(device_id)
        except Exception as exc:
            self._log("warning", f"Could not save device ID: {exc}")
        
        return device_id

    def _load_or_create(self) -> dict:
        try:
            if self.license_path.exists():
                with open(self.license_path, "r") as f:
                    data = json.load(f)
                return data
        except Exception as exc:
            self._log("warning", f"Failed to load license: {exc}")

        data = {
            "install_date": datetime.utcnow().isoformat(),
            "last_check": datetime.utcnow().isoformat(),
            "license_key": None,
            "plan": "trial",
            "validated": False,
            "last_validation": None
        }
        self._save(data)
        return data

    def _save(self, data: dict) -> None:
        try:
            self.license_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.license_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            self._log("warning", f"Failed to save license: {exc}")

    def days_remaining(self) -> int:
        """Get trial days remaining."""
        if self.is_licensed():
            return 9999  # Unlimited for licensed users
        
        install_date = self.data.get("install_date")
        if not install_date:
            return self.trial_days
        
        try:
            start = datetime.fromisoformat(install_date)
            end = start + timedelta(days=self.trial_days)
            remaining = (end - datetime.utcnow()).days
            return max(0, remaining)
        except Exception:
            return self.trial_days

    def is_trial_expired(self) -> bool:
        """Check if trial has expired."""
        if self.is_licensed():
            return False
        return self.days_remaining() <= 0

    def is_licensed(self) -> bool:
        """Check if user has a valid license."""
        return self.data.get("license_key") and self.data.get("validated")

    def validate_license_online(self, license_key: str) -> Dict:
        """Validate license key with online API."""
        if not requests:
            return {
                "valid": False,
                "error": "Network validation unavailable (missing requests library)"
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/validate-license",
                json={
                    "licenseKey": license_key,
                    "deviceId": self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "valid": False,
                    "error": f"Validation failed: {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {"valid": False, "error": "Validation timeout"}
        except requests.exceptions.ConnectionError:
            return {"valid": False, "error": "Cannot reach license server"}
        except Exception as exc:
            return {"valid": False, "error": str(exc)}

    def activate_license(self, license_key: str) -> tuple[bool, str]:
        """Activate a license key."""
        license_key = license_key.strip().upper()
        
        # Validate format
        if not license_key.startswith("PZDT-"):
            return False, "Invalid license key format"
        
        # Validate online
        result = self.validate_license_online(license_key)
        
        if result.get("valid"):
            # Save validated license
            self.data["license_key"] = license_key
            self.data["validated"] = True
            self.data["plan"] = result.get("plan", "unknown")
            self.data["last_validation"] = datetime.utcnow().isoformat()
            self._save(self.data)
            
            self._log("info", f"License activated: {license_key}")
            return True, f"License activated! Plan: {result.get('plan')}"
        else:
            error = result.get("error", "Unknown error")
            self._log("warning", f"License validation failed: {error}")
            return False, error

    def check_should_validate(self) -> bool:
        """Check if we should re-validate the license (every 7 days)."""
        if not self.is_licensed():
            return False
        
        last_validation = self.data.get("last_validation")
        if not last_validation:
            return True
        
        try:
            last = datetime.fromisoformat(last_validation)
            if datetime.utcnow() - last > timedelta(days=7):
                return True
        except Exception:
            return True
        
        return False

    def revalidate_license(self) -> bool:
        """Re-validate existing license."""
        if not self.is_licensed():
            return False
        
        license_key = self.data.get("license_key")
        result = self.validate_license_online(license_key)
        
        if result.get("valid"):
            self.data["last_validation"] = datetime.utcnow().isoformat()
            self._save(self.data)
            return True
        else:
            # License no longer valid - deactivate
            self._log("warning", "License validation failed - deactivating")
            self.data["validated"] = False
            self._save(self.data)
            return False

    def get_status(self) -> dict:
        """Get current license status."""
        return {
            "licensed": self.is_licensed(),
            "trial_expired": self.is_trial_expired(),
            "days_remaining": self.days_remaining(),
            "plan": self.data.get("plan", "trial"),
            "license_key": self.data.get("license_key"),
        }

    def record_check(self) -> None:
        """Record license check timestamp."""
        self.data["last_check"] = datetime.utcnow().isoformat()
        self._save(self.data)
