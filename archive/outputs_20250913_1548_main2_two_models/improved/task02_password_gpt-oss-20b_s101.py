#!/usr/bin/env python3
"""
user_registration.py

A minimal, secure user‑registration helper that stores usernames and
bcrypt‑hashed passwords in a file.  The file format is JSON‑lines
(one JSON object per line).  The module enforces a minimum password
length of 12 characters and never writes plaintext passwords to disk
or logs.

Security notes
--------------
* bcrypt automatically generates a per‑user salt and includes it in
  the resulting hash string.
* The password is never written to disk or printed; it is only
  encoded to UTF‑8 bytes for hashing.
* The user data file is opened in append‑plus mode and locked
  (on POSIX systems) to avoid race conditions when multiple
  processes register users concurrently.
* The module does not provide authentication; it only handles
  registration.  Authentication should be implemented separately
  using the same bcrypt hash comparison.

Dependencies
------------
* bcrypt  (install via `pip install bcrypt`)

Author: Senior Python Engineer
"""

import os
import json
import bcrypt
import sys
from typing import Optional

# Path to the file that stores user data.
# In a real application this should be a secure location with
# appropriate file permissions (e.g., 600).
USER_DB_PATH = "users.jsonl"

# Minimum password length requirement
MIN_PASSWORD_LENGTH = 12


def _acquire_file_lock(file_obj) -> None:
    """
    Acquire an exclusive lock on the file object.
    Works on POSIX systems via fcntl.  On Windows this is a no‑op.
    """
    try:
        import fcntl
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX)
    except ImportError:
        # fcntl is not available on Windows; skip locking.
        pass


def _release_file_lock(file_obj) -> None:
    """
    Release the lock acquired by _acquire_file_lock.
    """
    try:
        import fcntl
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
    except ImportError:
        pass


def _load_existing_usernames() -> set:
    """
    Load all usernames currently stored in the database file.
    Returns a set of usernames for quick lookup.
    """
    usernames = set()
    if not os.path.exists(USER_DB_PATH):
        return usernames

    with open(USER_DB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                usernames.add(record["username"])
            except (json.JSONDecodeError, KeyError):
                # Skip malformed lines; in production you might log this.
                continue
    return usernames


def register_user(username: str, password: str) -> bool:
    """
    Register a new user.

    Parameters
    ----------
    username : str
        Desired username.  Must be unique.
    password : str
        Plaintext password.  Must be at least MIN_PASSWORD_LENGTH
        characters long.

    Returns
    -------
    bool
        True if registration succeeded, False otherwise.

    Raises
    ------
    ValueError
        If the password is too short or the username already exists.
    """
    # Basic validation
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )

    # Ensure username is not already taken
    existing_usernames = _load_existing_usernames()
    if username in existing_usernames:
        raise ValueError(f"Username '{username}' is already taken.")

    # Hash the password with bcrypt (generates a per‑user salt)
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Prepare the record to write
    record = {
        "username": username,
        "hash": hashed.decode("utf-8"),  # Store as UTF‑8 string
    }

    # Write to the database file with an exclusive lock
    with open(USER_DB_PATH, "a", encoding="utf-8") as f:
        _acquire_file_lock(f)
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())  # Ensure data is written to disk
        _release_file_lock(f)

    return True


# --------------------------------------------------------------------------- #
# Example usage (for demonstration only; remove or guard in production)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python user_registration.py <username> <password>")
        sys.exit(1)

    user, pwd = sys.argv[1], sys.argv[2]
    try:
        if register_user(user, pwd):
            print(f"User '{user}' registered successfully.")
    except ValueError as e:
        print(f"Registration failed: {e}")
        sys.exit(1)