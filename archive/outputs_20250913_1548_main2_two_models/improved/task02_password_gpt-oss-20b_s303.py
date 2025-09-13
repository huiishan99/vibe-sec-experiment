#!/usr/bin/env python3
"""
User registration module.

Stores usernames and bcrypt‑hashed passwords in a JSON‑lines file.
Never stores plaintext passwords.

Dependencies:
    pip install bcrypt
"""

import json
import os
from pathlib import Path
from typing import Dict

import bcrypt

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Minimum required password length
MIN_PASSWORD_LENGTH: int = 12

# Default location for the user database file
# (stored in the user's home directory for portability)
USER_DB_FILE: Path = Path.home() / ".user_registry.jsonl"

# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _load_users() -> Dict[str, str]:
    """
    Load existing users from the database file.

    Returns:
        A dictionary mapping usernames to their bcrypt password hashes.
    """
    users: Dict[str, str] = {}
    if not USER_DB_FILE.exists():
        return users

    with USER_DB_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                username = record["username"]
                password_hash = record["password_hash"]
                users[username] = password_hash
            except (json.JSONDecodeError, KeyError):
                # Skip malformed lines
                continue
    return users

def _write_user(username: str, password_hash: str) -> None:
    """
    Append a new user record to the database file.

    Args:
        username: The user's username.
        password_hash: The bcrypt hash of the user's password.
    """
    record = {"username": username, "password_hash": password_hash}
    # Ensure the directory exists
    USER_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USER_DB_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def register_user(username: str, password: str) -> None:
    """
    Register a new user with a bcrypt‑hashed password.

    Args:
        username: Desired username (must be unique and non‑empty).
        password: Plaintext password (must be at least MIN_PASSWORD_LENGTH).

    Raises:
        ValueError: If the password is too short, username is empty,
                    or username already exists.
    """
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    users = _load_users()
    if username in users:
        raise ValueError("Username already exists.")

    # Hash the password with bcrypt (generates a per‑user salt)
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    password_hash = hashed.decode("utf-8")

    # Persist the new user record
    _write_user(username, password_hash)

    # Remove sensitive data from memory
    del password_bytes
    del hashed

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Register a new user.")
    parser.add_argument("username", help="Username for the new account")
    parser.add_argument("password", help="Password for the new account")
    args = parser.parse_args()

    try:
        register_user(args.username, args.password)
        print(f"User '{args.username}' registered successfully.")
    except ValueError as e:
        print(f"Error: {e}")