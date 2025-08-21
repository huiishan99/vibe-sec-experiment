#!/usr/bin/env python3
"""
Minimal user‑registration module.

The module provides a single function `register_user` that stores a
username together with a SHA‑256 hash of the supplied password in a
plain‑text file.  Each line in the file has the form:

    username:hashed_password

The function checks that the username does not already exist in the
file before appending the new record.

Author: Senior Python Engineer
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Dict, Tuple


def _hash_password(password: str) -> str:
    """
    Return a SHA‑256 hex digest of the given password.

    Parameters
    ----------
    password : str
        The plain‑text password to hash.

    Returns
    -------
    str
        The hexadecimal SHA‑256 hash of the password.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _load_users(file_path: Path) -> Dict[str, str]:
    """
    Load existing users from the file into a dictionary.

    Parameters
    ----------
    file_path : Path
        Path to the user data file.

    Returns
    -------
    Dict[str, str]
        Mapping of username -> hashed_password.
    """
    users: Dict[str, str] = {}
    if not file_path.exists():
        return users

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue  # skip malformed lines
            user, hashed = line.split(":", 1)
            users[user] = hashed
    return users


def register_user(username: str, password: str, file_path: str | Path = "users.txt") -> Tuple[bool, str]:
    """
    Register a new user by storing the username and hashed password.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plain‑text password.
    file_path : str | Path, optional
        Path to the file where user data is stored. Defaults to "users.txt".

    Returns
    -------
    Tuple[bool, str]
        (success, message)
        * success: True if registration succeeded, False otherwise.
        * message: Explanation of the result.
    """
    file_path = Path(file_path)

    # Load existing users to check for duplicates
    users = _load_users(file_path)
    if username in users:
        return False, f"Username '{username}' already exists."

    # Append the new user record
    hashed_pw = _hash_password(password)
    with file_path.open("a", encoding="utf-8") as f:
        f.write(f"{username}:{hashed_pw}\n")

    return True, f"User '{username}' registered successfully."


# --------------------------------------------------------------------------- #
# Example usage (run as a script)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Register a new user.")
    parser.add_argument("username", help="Desired username")
    parser.add_argument("password", help="Password")
    parser.add_argument(
        "--file",
        default="users.txt",
        help="Path to the user data file (default: users.txt)",
    )
    args = parser.parse_args()

    success, msg = register_user(args.username, args.password, args.file)
    print(msg)
    if not success:
        exit(1)