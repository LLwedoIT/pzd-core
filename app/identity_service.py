"""
Identity Service - Windows Hello biometric verification

Uses UserConsentVerifier when available. Falls back to unavailable state if
Windows Hello or winrt bindings are not present.
"""

import asyncio
from typing import Optional


class IdentityService:
    """Optional Windows Hello verification service."""

    def __init__(self, logger=None):
        self.logger = logger
        self._available = False
        self._availability_reason: Optional[str] = None
        self._initialize()

    def _log(self, level: str, message: str):
        if self.logger:
            log_fn = getattr(self.logger, level, None)
            if log_fn:
                log_fn(message, "IdentityService")
                return
        print(f"[IdentityService] {message}")

    def _initialize(self):
        try:
            from winrt.windows.security.credentials.ui import UserConsentVerifier  # type: ignore
            self._UserConsentVerifier = UserConsentVerifier
            self._available = True
            self._availability_reason = "Available"
        except Exception as exc:
            self._available = False
            self._availability_reason = str(exc)
            self._log("warning", "Windows Hello not available")

    def is_available(self) -> bool:
        return self._available

    def availability_reason(self) -> str:
        return self._availability_reason or "Unknown"

    async def _request_verification_async(self, message: str) -> bool:
        result = await self._UserConsentVerifier.request_verification_async(message)
        # UserConsentVerificationResult.Verified == 0
        return int(result) == 0

    def verify_user(self, message: str = "Verify your identity") -> bool:
        """
        Prompt Windows Hello verification. Returns True if verified.
        """
        if not self._available:
            return False
        try:
            try:
                return asyncio.run(self._request_verification_async(message))
            except RuntimeError:
                loop = asyncio.new_event_loop()
                try:
                    return loop.run_until_complete(self._request_verification_async(message))
                finally:
                    loop.close()
        except Exception as exc:
            self._log("warning", f"Verification failed: {exc}")
            return False
