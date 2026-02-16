"""
Configuration Service - Load and manage user settings from config.json

Handles loading, validation, default values, and hot reloading of settings.
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigService:
    """
    Manages application configuration from config.json file.
    
    Provides safe access to settings with type validation and defaults.
    """
    
    # Default configuration values (in case config.json is missing)
    DEFAULTS = {
        "lockTimeoutSeconds": 60,
        "enableHidDetection": True,
        "enableCameraDetection": True,
        "enableAudioDetection": False,
        "enableAppAwareness": True,
        "enableNetworkControl": False,
        "enableBiometricVerification": False,
        "cameraSensitivity": 350,
        "pz_reach": 0.7,
        "proximityMin": 50,
        "enableGuardianMode": False,
        "guardianAutoEnable": False,
        "enableGlobalHotkey": True,
        "globalHotkeyCombo": "ctrl+alt+shift+x",
        "enableLogging": True,
        "logLevel": "INFO",
        "logPath": "logs/",
        "logMaxFiles": 10,
        "enableAuditLog": True,
        "auditLogPath": "audit_log.json",
        "enableNetworkWiFiControl": False,
        "enableLicenseCheck": True,
        "trialDays": 7,
        "purchaseUrl": "https://pzdetector.com/pricing",
        "licenseApiUrl": "https://api.pzdetector.com",
        "identityPromptMessage": "Confirm you're still here",
        "warningThresholdSeconds": 10,
        "idleThresholdSeconds": 50,
        "updateCheckInterval": 86400,
        "enableTelemetry": False,
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration service.
        
        Args:
            config_path: Path to config.json file (relative to app directory)
        """
        self.config_path = Path(config_path)
        self.config = {}
        self._load_config()
    
    def _load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                # Merge with defaults (loaded config overrides defaults)
                self.config = {**self.DEFAULTS, **loaded}
                print(f"[Config] Loaded from {self.config_path}")
                return True
            else:
                print(f"[Config] File not found, using defaults")
                self.config = self.DEFAULTS.copy()
                return False
        except Exception as e:
            print(f"[Config] Error loading config: {e}, using defaults")
            self.config = self.DEFAULTS.copy()
            return False
    
    def reload(self) -> bool:
        """
        Reload configuration from file (for hot reload).
        
        Returns:
            bool: True if reload successful
        """
        self._load_config()
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default if default is not None else self.DEFAULTS.get(key))
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value in memory (not persisted).
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            bool: True if save successful
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"[Config] Saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
            return False
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        val = self.get(key)
        try:
            return int(val) if val is not None else default
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        val = self.get(key)
        try:
            return float(val) if val is not None else default
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        val = self.get(key)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ('true', '1', 'yes', 'on')
        return default
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get a string configuration value."""
        val = self.get(key)
        return str(val) if val is not None else default
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get entire configuration as dictionary.
        
        Returns:
            Dict of all configuration values
        """
        return self.config.copy()
    
    def validate(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            bool: True if all required keys present and types valid
        """
        required_keys = set(self.DEFAULTS.keys())
        present_keys = set(self.config.keys())
        
        if not required_keys.issubset(present_keys):
            missing = required_keys - present_keys
            print(f"[Config] Missing keys: {missing}")
            return False
        
        return True
    
    def get_missing_keys(self) -> list:
        """
        Get list of keys that are in defaults but not in loaded config.
        
        Returns:
            List of missing keys
        """
        required_keys = set(self.DEFAULTS.keys())
        present_keys = set(self.config.keys())
        return list(required_keys - present_keys)
