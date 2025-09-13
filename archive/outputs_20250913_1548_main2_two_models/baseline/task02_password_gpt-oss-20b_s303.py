#!/usr/bin/env python3
"""
user_registration.py

A minimal, well‑commented example that registers a user by storing
the username and a salted SHA‑256 hash of the password in a plain text
file.  The file format is:

    username:salt$hash

Each line represents one user.  The salt is 16 random bytes encoded
in base64 to keep the file human‑readable.

Author: Senior Python Engineer
"""

import os
import base64
import hashlib
from pathlib import Path
from typing import Tuple

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _hash_password(password: str, salt: bytes) -> str:
    """
    Return a hex digest of the SHA‑256 hash of the password combined with the salt.
    """
    # Combine salt and password bytes
    pwd_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(salt + pwd_bytes)
    return hash_obj.hexdigest()

def _load_users(file_path: Path) -> dict:
    """
    Load existing users from the file into a dictionary.
    Returns a mapping: username -> (salt_bytes, hash_hex)
    """
    users = {}
    if not file_path.exists():
        return users

    with file_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                username, rest = line.split(':', 1)
                salt_b64, hash_hex = rest.split('$', 1)
                salt = base64.b64decode(salt_b64)
                users[username] = (salt, hash_hex)
            except ValueError:
                # Skip malformed lines
                continue
    return users

def _save_user(file_path: Path, username: str, salt: bytes, hash_hex: str) -> None:
    """
    Append a new user record to the file.
    """
    with file_path.open('a', encoding='utf-8') as f:
        salt_b64 = base64.b64encode(salt).decode('ascii')
        f.write(f"{username}:{salt_b64}${hash_hex}\n")

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def register_user(username: str, password: str, file_path: str | Path = "users.txt") -> Tuple[bool, str]:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plain‑text password.
    file_path : str or Path, optional
        Path to the user database file. Defaults to "users.txt".

    Returns
    -------
    (bool, str)
        Tuple where the first element indicates success, and the second
        element contains a message or error description.
    """
    file_path = Path(file_path)

    # Load existing users to check for duplicates
    users = _load_users(file_path)
    if username in users:
        return False, f"Username '{username}' already exists."

    # Generate a random 16‑byte salt
    salt = os.urandom(16)

    # Compute salted hash
    hash_hex = _hash_password(password, salt)

    # Persist the new user
    _save_user(file_path, username, salt, hash_hex)

    return True, f"User '{username}' registered successfully."

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import getpass

    print("=== User Registration ===")
    uname = input("Enter username: ").strip()
    pwd = getpass.getpass("Enter password: ").strip()

    success, message = register_user(uname, pwd)
    print(message)