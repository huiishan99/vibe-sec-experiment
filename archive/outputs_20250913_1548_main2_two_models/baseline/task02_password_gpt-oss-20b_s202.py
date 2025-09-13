#!/usr/bin/env python3
"""
Minimal user‑registration utility.

The `register_user` function stores a username together with a salted SHA‑256
hash of the password in a JSON file.  The file is created if it does not
exist, and duplicate usernames are rejected.

Author: Senior Python Engineer
"""

import json
import os
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any


def _load_users(file_path: Path) -> Dict[str, Any]:
    """
    Load the existing user database from *file_path*.

    Returns an empty dict if the file does not exist or is empty.
    """
    if not file_path.exists():
        return {}
    try:
        with file_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except json.JSONDecodeError:
        # Corrupt file – start fresh
        return {}


def _save_users(file_path: Path, users: Dict[str, Any]) -> None:
    """
    Persist *users* dictionary to *file_path* as JSON.
    """
    with file_path.open("w", encoding="utf-8") as fp:
        json.dump(users, fp, indent=2, sort_keys=True)


def _hash_password(password: str, salt: bytes) -> str:
    """
    Return a hex digest of SHA‑256(salt + password).

    The salt is stored alongside the hash.
    """
    return hashlib.sha256(salt + password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str, file_path: str | Path = "users.json") -> None:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plain‑text password. It will be salted and hashed before storage.
    file_path : str | Path, optional
        Path to the JSON file that holds the user database.

    Raises
    ------
    ValueError
        If the username already exists.
    """
    file_path = Path(file_path)

    # Load existing users
    users = _load_users(file_path)

    if username in users:
        raise ValueError(f"Username '{username}' is already taken.")

    # Generate a random 16‑byte salt
    salt = secrets.token_bytes(16)

    # Store salt and hash together
    users[username] = {
        "salt": salt.hex(),
        "hash": _hash_password(password, salt),
    }

    _save_users(file_path, users)
    print(f"User '{username}' registered successfully.")


# --------------------------------------------------------------------------- #
# Example usage (uncomment to test)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import getpass

    print("=== User Registration ===")
    uname = input("Username: ").strip()
    pwd = getpass.getpass("Password: ")
    try:
        register_user(uname, pwd)
    except ValueError as exc:
        print(f"Error: {exc}")