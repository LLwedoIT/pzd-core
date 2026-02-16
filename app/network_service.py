"""
Network Service - Manage network adapter state for security

Uses netsh to disable/enable active network adapters. Requires admin.
"""

import subprocess
import ctypes
from typing import List


class NetworkService:
    """Disable and re-enable network adapters using netsh."""

    def __init__(self, logger=None):
        self.logger = logger
        self._disabled_adapters: List[str] = []

    def _is_admin(self) -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def _log(self, level: str, message: str):
        if self.logger:
            log_fn = getattr(self.logger, level, None)
            if log_fn:
                log_fn(message, "NetworkService")
                return
        print(f"[NetworkService] {message}")

    def _get_active_adapters(self) -> List[str]:
        """Return a list of enabled adapter names."""
        try:
            result = subprocess.run(
                ["netsh", "interface", "show", "interface"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                self._log("warning", f"netsh error: {result.stderr.strip()}")
                return []

            adapters = []
            lines = result.stdout.splitlines()
            for line in lines:
                if "Enabled" in line:
                    # Expected format: Admin State  State  Type  Interface Name
                    parts = line.split()
                    if len(parts) >= 4:
                        name = " ".join(parts[3:])
                        adapters.append(name)
            return adapters
        except Exception as exc:
            self._log("error", f"Failed to list adapters: {exc}")
            return []

    def disable_all(self) -> bool:
        """Disable all enabled network adapters."""
        if not self._is_admin():
            self._log("warning", "Admin privileges required to disable adapters")
            return False

        adapters = self._get_active_adapters()
        if not adapters:
            self._log("info", "No active adapters found")
            return True

        self._disabled_adapters.clear()
        success = True
        for name in adapters:
            cmd = ["netsh", "interface", "set", "interface", name, "admin=DISABLED"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                self._disabled_adapters.append(name)
                self._log("info", f"Disabled adapter: {name}")
            else:
                success = False
                self._log("warning", f"Failed to disable {name}: {result.stderr.strip()}")
        return success

    def enable_all(self) -> bool:
        """Re-enable adapters disabled by this service."""
        if not self._is_admin():
            self._log("warning", "Admin privileges required to enable adapters")
            return False

        if not self._disabled_adapters:
            self._log("info", "No adapters to re-enable")
            return True

        success = True
        for name in list(self._disabled_adapters):
            cmd = ["netsh", "interface", "set", "interface", name, "admin=ENABLED"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                self._log("info", f"Enabled adapter: {name}")
                self._disabled_adapters.remove(name)
            else:
                success = False
                self._log("warning", f"Failed to enable {name}: {result.stderr.strip()}")
        return success
