#!/usr/bin/env python3
"""
User registration module.

Stores usernames and bcrypt‑hashed passwords in a JSON file.
Never stores plaintext passwords and enforces a minimum password length.
"""

import os
import json
import bcrypt

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Path to the user database file.  Adjust as needed.
USER_DB_PATH = "user_db.json"

# Minimum required password length
MIN_PASSWORD_LENGTH = 12

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _load_user_db(path: str = USER_DB_PATH) -> dict:
    """
    Load the user database from a JSON file.

    Returns an empty dict if the file does not exist or is corrupted.
    """
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file – start fresh
            return {}

def _save_user_db(db: dict, path: str = USER_DB_PATH) -> None:
    """
    Persist the user database to a JSON file.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True)

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def register_user(username: str, password: str, path: str = USER_DB_PATH) -> None:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username. Must be unique.
    password : str
        Plaintext password. Must be at least MIN_PASSWORD_LENGTH characters.
    path : str, optional
        Path to the user database file.

    Raises
    ------
    ValueError
        If the password is too short, or the username already exists.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )

    db = _load_user_db(path)

    if username in db:
        raise ValueError("Username already exists")

    # Generate a per‑user salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Store the hashed password as a UTF‑8 string
    db[username] = hashed.decode("utf-8")

    _save_user_db(db, path)

def verify_user(username: str, password: str, path: str = USER_DB_PATH) -> bool:
    """
    Verify a user's credentials.

    Returns True if the password matches the stored hash.
    """
    db = _load_user_db(path)
    stored_hash = db.get(username)
    if not stored_hash:
        return False

    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))

# --------------------------------------------------------------------------- #
# Demo / Test
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Example usage
    try:
        register_user("alice", "supersecurepassword123")
        print("User 'alice' registered successfully.")
    except ValueError as e:
        print(f"Registration failed: {e}")

    # Verify credentials
    if verify_user("alice", "supersecurepassword123"):
        print("Login successful.")
    else:
        print("Login failed.")