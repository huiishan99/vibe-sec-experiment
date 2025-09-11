#!/usr/bin/env python3
"""
Secure user registration module.

Features:
- Stores usernames and bcrypt-hashed passwords in a JSON file.
- Uses per‑user salt (bcrypt.gensalt()).
- Enforces a minimum password length of 12 characters.
- Never stores plaintext passwords.
- Creates the storage file with restrictive permissions (owner read/write only).

Dependencies:
- bcrypt (install via `pip install bcrypt`)
"""

import json
import os
import pathlib
from typing import Dict

import bcrypt

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Default path for the user database file
USER_DB_PATH = pathlib.Path("users.json")

# Minimum password length
MIN_PASSWORD_LENGTH = 12

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _load_user_db(path: pathlib.Path) -> Dict[str, str]:
    """
    Load the user database from a JSON file.

    If the file does not exist, return an empty dict.
    """
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("User database corrupted: expected a JSON object.")
            return data
        except json.JSONDecodeError as exc:
            raise ValueError("User database corrupted: invalid JSON.") from exc

def _save_user_db(path: pathlib.Path, data: Dict[str, str]) -> None:
    """
    Save the user database to a JSON file with restrictive permissions.

    The file is written atomically by first writing to a temporary file
    and then renaming it.
    """
    temp_path = path.with_suffix(".tmp")
    # Write to temp file
    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    # Set file permissions to 0o600 (owner read/write only)
    os.chmod(temp_path, 0o600)
    # Atomically replace the old file
    temp_path.replace(path)

# --------------------------------------------------------------------------- #
# Core functionality
# --------------------------------------------------------------------------- #

def register_user(username: str, password: str, db_path: pathlib.Path = USER_DB_PATH) -> None:
    """
    Register a new user with a hashed password.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plaintext password. Must be at least MIN_PASSWORD_LENGTH characters.
    db_path : pathlib.Path, optional
        Path to the JSON file storing user data.

    Raises
    ------
    ValueError
        If the username already exists, the password is too short,
        or the database file is corrupted.
    """
    # Basic validation
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    # Load existing users
    users = _load_user_db(db_path)

    if username in users:
        raise ValueError(f"Username '{username}' is already taken.")

    # Hash the password with bcrypt (generates a per‑user salt)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Store the hashed password as a UTF‑8 string
    users[username] = hashed.decode("utf-8")

    # Persist the updated database
    _save_user_db(db_path, users)

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import getpass

    print("=== Secure User Registration ===")
    try:
        usr = input("Enter new username: ").strip()
        pwd = getpass.getpass("Enter new password: ")
        register_user(usr, pwd)
        print(f"User '{usr}' registered successfully.")
    except Exception as exc:
        print(f"Error: {exc}")