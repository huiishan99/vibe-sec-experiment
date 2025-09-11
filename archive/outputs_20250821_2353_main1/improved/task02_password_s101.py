#!/usr/bin/env python3
"""
user_registration.py

A minimal, secure user registration module that stores usernames and
bcrypt‑hashed passwords in a JSON file.  Passwords are never stored in
plain text and each user gets a unique per‑user salt via bcrypt.gensalt().
The module enforces a minimum password length of 12 characters.

Security notes
--------------
* bcrypt is used for hashing – it is slow by design and includes a
  per‑user salt automatically.
* The JSON file is opened with an exclusive lock (fcntl) to avoid
  race conditions on POSIX systems.
* File permissions are set to 0o600 (owner read/write only) to prevent
  other users from reading the password hashes.
* Usernames are stored as plain strings; no special sanitisation is
  performed beyond checking that the username is non‑empty.
"""

import bcrypt
import json
import os
import sys
import fcntl
from pathlib import Path
from typing import Dict

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _ensure_file(file_path: Path) -> None:
    """
    Ensure that the user file exists and has secure permissions.
    """
    if not file_path.exists():
        # Create an empty JSON file
        file_path.write_text("{}", encoding="utf-8")
    # Set file permissions to owner read/write only
    os.chmod(file_path, 0o600)

def _load_users(file_path: Path) -> Dict[str, str]:
    """
    Load the user dictionary from the JSON file.
    Returns an empty dict if the file is empty.
    """
    with file_path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_users(users: Dict[str, str], file_path: Path) -> None:
    """
    Write the user dictionary to the JSON file atomically.
    """
    # Write to a temporary file first
    tmp_path = file_path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, sort_keys=True)
    # Replace the original file atomically
    tmp_path.replace(file_path)

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def register_user(username: str, password: str, file_path: str = "users.json") -> None:
    """
    Register a new user with the given username and password.

    Parameters
    ----------
    username : str
        The desired username. Must be non-empty and unique.
    password : str
        The user's password. Must be at least 12 characters long.
    file_path : str, optional
        Path to the JSON file that stores user data. Defaults to "users.json".

    Raises
    ------
    ValueError
        If the username is empty, already taken, or the password is too short.
    IOError
        If the user file cannot be accessed or written to.
    """
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")

    path = Path(file_path).expanduser().resolve()
    _ensure_file(path)

    # Open the file with an exclusive lock to prevent concurrent writes
    with path.open("r+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}

        if username in users:
            raise ValueError(f"Username '{username}' is already taken.")

        # Hash the password with bcrypt (includes a unique salt)
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        users[username] = hashed.decode("utf-8")

        # Move file pointer to the beginning and truncate
        f.seek(0)
        f.truncate()
        json.dump(users, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f, fcntl.LOCK_UN)

# --------------------------------------------------------------------------- #
# Example usage / simple test
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Simple command‑line interface for testing
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <username> <password>", file=sys.stderr)
        sys.exit(1)

    user, pwd = sys.argv[1], sys.argv[2]
    try:
        register_user(user, pwd)
        print(f"User '{user}' registered successfully.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)