#!/usr/bin/env python3
"""
Secure file reader.

This module defines a single function, `read_user_file`, that prompts the user
for a file path, validates the path against a fixed base directory, and
returns the file's text content.  The function enforces the following
security constraints:

* The supplied path must be **relative** – absolute paths are rejected.
* The path must not contain any "`..`" components – directory traversal is
  disallowed.
* After resolving symlinks, the final path must reside inside the allowed
  base directory.
* Only text files are read (UTF‑8 encoding).  Binary files will raise a
  decoding error.

The base directory is created automatically if it does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# The directory that is allowed to contain readable files.
# Adjust this path as needed for your environment.
BASE_DIR: Path = Path(__file__).parent / "allowed_files"

# Ensure the base directory exists.
BASE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Core functionality
# --------------------------------------------------------------------------- #

def read_user_file() -> str:
    """
    Prompt the user for a relative file path, validate it, and return its
    text content.

    Returns
    -------
    str
        The decoded text content of the requested file.

    Raises
    ------
    ValueError
        If the input path is absolute, empty, or contains '..'.
    FileNotFoundError
        If the resolved path does not exist or is not a file.
    PermissionError
        If the file cannot be opened due to insufficient permissions.
    UnicodeDecodeError
        If the file cannot be decoded as UTF‑8.
    """
    # Prompt the user for a relative file path.
    user_input = input("Enter the relative path of the file to read: ").strip()

    # Reject empty input.
    if not user_input:
        raise ValueError("No path provided.")

    # Reject absolute paths.
    if Path(user_input).is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    # Reject paths that contain '..' components.
    if ".." in Path(user_input).parts:
        raise ValueError("Path traversal is not allowed.")

    # Resolve the target path relative to the allowed base directory.
    target_path = (BASE_DIR / user_input).resolve()

    # Ensure the resolved path is still inside BASE_DIR.
    try:
        target_path.relative_to(BASE_DIR.resolve())
    except ValueError:
        raise ValueError("Resolved path is outside the allowed base directory.")

    # Verify that the target exists and is a regular file.
    if not target_path.is_file():
        raise FileNotFoundError(f"File not found: {target_path}")

    # Read and return the file content as UTF‑8 text.
    with target_path.open("r", encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------------- #
# Demo / CLI entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    try:
        content = read_user_file()
        print("\n--- File Content ---\n")
        print(content)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)