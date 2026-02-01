import json
import os
import hashlib
from locales.manager import WORK_DIR

AUTH_FILE = os.path.join(WORK_DIR, "users.json")


class AuthManager:
    def __init__(self):
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(AUTH_FILE):
            return {}
        try:
            with open(AUTH_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_users(self):
        with open(AUTH_FILE, "w") as f:
            json.dump(self.users, f)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        if username in self.users:
            return False, "auth_err_exists"

        self.users[username] = self._hash_password(password)
        self._save_users()
        return True, "auth_success_reg"

    def login(self, username, password):
        if username not in self.users:
            return False, "auth_err_invalid"

        if self.users[username] == self._hash_password(password):
            return True, "Success"
        else:
            return False, "auth_err_invalid"