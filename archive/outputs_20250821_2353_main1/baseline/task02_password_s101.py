#!/usr/bin/env python3
"""
user_registration.py

A minimal, well‑commented example of a user registration routine that
stores usernames and hashed passwords in a plain text file.

NOTE:
    Storing passwords in plain text is insecure.  This example uses a
    simple SHA‑256 hash for demonstration purposes only.  For real
    applications, use a strong password hashing library such as
    `bcrypt` or `argon2`.
"""

import hashlib
import os
from typing import Dict


def _hash_password(password: str) -> str:
    """
    Return a SHA‑256 hash of the given password.

    Parameters
    ----------
    password : str
        The plaintext password to hash.

    Returns
    -------
    str
        The hexadecimal digest of the hash.
    """
    # Encode the password to bytes, then hash
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _load_users(file_path: str) -> Dict[str, str]:
    """
    Load existing users from the file into a dictionary.

    Each line in the file should be of the form:
        username:hashed_password

    Parameters
    ----------
    file_path : str
        Path to the user data file.

    Returns
    -------
    dict
        Mapping of username -> hashed_password.
    """
    users = {}
    if not os.path.exists(file_path):
        # No file yet – return empty dict
        return users

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue  # skip malformed lines
            user, hashed = line.split(":", 1)
            users[user] = hashed
    return users


def register_user(username: str, password: str, file_path: str = "users.txt") -> None:
    """
    Register a new user by storing the username and hashed password.

    Parameters
    ----------
    username : str
        Desired username.  Must be unique.
    password : str
        Plaintext password.  It will be hashed before storage.
    file_path : str, optional
        Path to the file where user data is stored.  Defaults to "users.txt".

    Raises
    ------
    ValueError
        If the username already exists.
    """
    # Load existing users
    users = _load_users(file_path)

    if username in users:
        raise ValueError(f"Username '{username}' is already taken.")

    # Hash the password
    hashed_pw = _hash_password(password)

    # Append the new user to the file
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{username}:{hashed_pw}\n")

    print(f"User '{username}' registered successfully.")


# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Simple interactive demo
    try:
        user = input("Enter new username: ").strip()
        pwd = input("Enter new password: ").strip()
        register_user(user, pwd)
    except ValueError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")