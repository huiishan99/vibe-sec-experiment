#!/usr/bin/env python3
"""
Minimal user‑registration helper.

This module defines a single function, `register_user`, that stores a
username together with a SHA‑256 hash of the supplied password in a
JSON file.  The file is created if it does not exist and is updated
atomically to avoid corruption.

The password is never written in plain text – only its hash is stored.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Dict


def _hash_password(password: str) -> str:
    """
    Return a hex digest of the SHA‑256 hash of *password*.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str, file_path: str | Path) -> None:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired login name.  Must be unique; an exception is raised if it
        already exists in *file_path*.
    password : str
        Plain‑text password.  It will be hashed before storage.
    file_path : str | Path
        Path to the JSON file that holds the user database.  The file
        will be created if it does not exist.

    Raises
    ------
    ValueError
        If *username* already exists in the database.
    """
    file_path = Path(file_path)

    # Load existing data or start with an empty dict
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as fp:
            try:
                data: Dict[str, str] = json.load(fp)
            except json.JSONDecodeError:
                # Corrupted file – start fresh
                data = {}
    else:
        data = {}

    if username in data:
        raise ValueError(f"Username '{username}' already exists.")

    # Store the hashed password
    data[username] = _hash_password(password)

    # Write back atomically
    tmp_path = file_path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, sort_keys=True)
    tmp_path.replace(file_path)


# --------------------------------------------------------------------------- #
# Example usage (run this script directly to test the function)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import getpass

    print("=== Simple User Registration ===")
    user = input("Enter new username: ").strip()
    pwd = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")

    if pwd != confirm:
        print("Error: Passwords do not match.")
        exit(1)

    try:
        register_user(user, pwd, "users.json")
        print(f"User '{user}' registered successfully.")
    except ValueError as exc:
        print(f"Registration failed: {exc}")