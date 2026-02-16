"""
License Service - Trial management for PZDetector

Stores install date locally and enforces a trial period.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class LicenseService:
    """Simple local trial license service."""

    def __init__(self, trial_days: int = 7, purchase_url: str = "", logger=None):
        self.trial_days = trial_days
        self.purchase_url = purchase_url
        self.logger = logger
        self.license_path = self._default_license_path()
        self.data = self._load_or_create()

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
            "last_check": datetime.utcnow().isoformat()
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
        return self.days_remaining() <= 0

    def record_check(self) -> None:
        self.data["last_check"] = datetime.utcnow().isoformat()
        self._save(self.data)
