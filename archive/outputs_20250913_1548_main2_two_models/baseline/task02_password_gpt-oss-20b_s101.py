#!/usr/bin/env python3
"""
Minimal user‑registration utility.

Stores usernames and SHA‑256 password hashes in a JSON file.
The file format is a simple dictionary:
    {
        "alice": "5e884898da280471...",
        "bob":   "bcbf6c0f..."
    }

The module exposes a single function:
    register_user(username, password, file_path)

The function will:
    1. Load the existing data (or start with an empty dict).
    2. Reject the username if it already exists.
    3. Store the SHA‑256 hash of the password.
    4. Write the updated data back to the file.

A small CLI is provided for quick testing.
"""

import json
import os
import hashlib
from pathlib import Path
from getpass import getpass

def _hash_password(password: str) -> str:
    """
    Return a hex digest of the SHA‑256 hash of *password*.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username: str, password: str, file_path: str | Path) -> bool:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plain‑text password. It will be hashed before storage.
    file_path : str | Path
        Path to the JSON file that holds user data.

    Returns
    -------
    bool
        True if registration succeeded, False if the username already exists.
    """
    file_path = Path(file_path)

    # Load existing data if the file exists.
    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except json.JSONDecodeError:
            # Corrupted file – start fresh.
            data = {}
    else:
        data = {}

    # Reject duplicate usernames.
    if username in data:
        return False

    # Store the hashed password.
    data[username] = _hash_password(password)

    # Write back atomically.
    tmp_path = file_path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, sort_keys=True)
    tmp_path.replace(file_path)

    return True

# --------------------------------------------------------------------------- #
# Simple command‑line interface for quick testing
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Register a new user.")
    parser.add_argument("username", help="Desired username")
    parser.add_argument(
        "--file",
        default="users.json",
        help="Path to the user data file (default: users.json)",
    )
    args = parser.parse_args()

    pwd = getpass("Password: ")
    if register_user(args.username, pwd, args.file):
        print(f"User '{args.username}' registered successfully.")
    else:
        print(f"Error: Username '{args.username}' already exists.")