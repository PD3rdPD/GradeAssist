"""Local account storage for GradeAssist.

Passwords are never written to disk in plain text. Each password is hashed
with PBKDF2-HMAC-SHA256 and a unique random salt before storage.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from pathlib import Path

PBKDF2_ITERATIONS = 200_000


class AccountManager:
    """Create and authenticate local GradeAssist user accounts."""

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)

    def _load(self) -> dict:
        if not self.storage_path.exists():
            return {"accounts": {}}

        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {"accounts": {}}

        if not isinstance(data, dict):
            return {"accounts": {}}

        accounts = data.get("accounts")

        if not isinstance(accounts, dict):
            data["accounts"] = {}

        return data

    def _save(self, data: dict) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def _normalize_username(username: str) -> str:
        return username.strip().lower()

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )

    def create_account(self, username: str, password: str) -> str:
        username = self._normalize_username(username)

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters.")

        if " " in username:
            raise ValueError("Username cannot contain spaces.")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

        data = self._load()

        if username in data["accounts"]:
            raise ValueError("That username already exists.")

        salt = secrets.token_bytes(16)
        password_hash = self._hash_password(password, salt)

        data["accounts"][username] = {
            "salt": salt.hex(),
            "password_hash": password_hash.hex(),
            "profile": {
                "student_name": "",
            },
        }

        self._save(data)
        return username

    def authenticate(self, username: str, password: str) -> bool:
        username = self._normalize_username(username)
        data = self._load()

        account = data["accounts"].get(username)

        if not account:
            return False

        try:
            salt = bytes.fromhex(account["salt"])
            expected_hash = bytes.fromhex(account["password_hash"])
        except (KeyError, TypeError, ValueError):
            return False

        actual_hash = self._hash_password(password, salt)

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    def get_profile(self, username: str) -> dict:
        username = self._normalize_username(username)
        data = self._load()

        account = data["accounts"].get(username, {})
        profile = account.get("profile", {})

        return dict(profile) if isinstance(profile, dict) else {}

    def save_profile(self, username: str, **updates) -> None:
        username = self._normalize_username(username)
        data = self._load()

        account = data["accounts"].get(username)

        if not account:
            raise ValueError("Account not found.")

        profile = account.setdefault("profile", {})
        profile.update(updates)

        self._save(data)