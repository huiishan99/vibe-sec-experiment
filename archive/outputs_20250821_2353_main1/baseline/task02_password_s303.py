#!/usr/bin/env python3
"""
Simple user‑registration module.

Stores usernames and SHA‑256 password hashes in a plain‑text file.
Each line in the file has the format:
    username:hashed_password

The module provides a single function:
    register_user(username, password, filename='users.txt')

The function checks that the username is not already taken and
appends the new user to the file if it is free.
"""

import hashlib
import os
from typing import Optional


def _hash_password(password: str) -> str:
    """
    Return the SHA‑256 hex digest of the given password.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _user_exists(username: str, filename: str) -> bool:
    """
    Return True if the username already exists in the file.
    """
    if not os.path.exists(filename):
        return False

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            stored_user, _ = line.rstrip("\n").split(":", 1)
            if stored_user == username:
                return True
    return False


def register_user(username: str, password: str, filename: str = "users.txt") -> bool:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plain‑text password. It will be stored as a SHA‑256 hash.
    filename : str, optional
        Path to the file where users are stored. Defaults to 'users.txt'.

    Returns
    -------
    bool
        True if registration succeeded, False if the username is already taken.
    """
    if _user_exists(username, filename):
        print(f"Error: Username '{username}' is already taken.")
        return False

    hashed = _hash_password(password)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{username}:{hashed}\n")

    print(f"User '{username}' registered successfully.")
    return True


# --------------------------------------------------------------------------- #
# Example usage (run this file directly to test the registration function)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import getpass

    print("=== User Registration ===")
    user = input("Enter username: ").strip()
    pwd = getpass.getpass("Enter password: ").strip()
    register_user(user, pwd)