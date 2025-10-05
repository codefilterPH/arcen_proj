from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import redirect
from django.urls import reverse
import time


class TokenValidator:
    def __init__(self, token: str, uid: str, expiry_seconds: int = 900, debug: bool = False):
        self.token = token
        self.uid = str(uid)
        self.expiry_seconds = expiry_seconds
        self.signer = TimestampSigner()
        self.debug = debug  # NEW: flag to toggle console logging

    def _get_token_parts(self):
        try:
            parts = self.token.split(':')
            if len(parts) != 3:
                return None, None
            unsigned_value = parts[0]
            timestamp = int(parts[1])  # <- this may fail if parts[1] is not a valid int
            return unsigned_value, timestamp
        except Exception:
            return None, None

    def time_remaining(self):
        _, timestamp = self._get_token_parts()
        if timestamp is None:
            return None
        remaining = self.expiry_seconds - (int(time.time()) - timestamp)
        return max(0, remaining)

    def is_valid(self):
        try:
            unsigned_uid = self.signer.unsign(self.token, max_age=self.expiry_seconds)
            valid = str(unsigned_uid) == self.uid
            if valid and self.debug:
                remaining = self.time_remaining()
                print(f"🔐 Token valid. Time left: {remaining} seconds")
            return valid
        except (SignatureExpired, BadSignature):
            if self.debug:
                print("❌ Token invalid or expired.")
            return False

    def validate_or_redirect(self):
        if not self.is_valid():
            return redirect(reverse('authentication:token_expired_view'))
        return None
