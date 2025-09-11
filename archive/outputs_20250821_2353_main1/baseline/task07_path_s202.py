#!/usr/bin/env python3
"""
Utility to read a file whose path is supplied by the user.

The module exposes a single function `read_file_from_user()` that:
1. Prompts the user for a file path.
2. Opens the file in text mode (UTF‑8 encoding).
3. Returns the file's entire content as a string.

The function propagates standard I/O exceptions so that callers can
handle errors (e.g., file not found, permission denied) as needed.
"""

from __future__ import annotations
from typing import Optional


def read_file_from_user() -> str:
    """
    Prompt the user for a file path, read the file, and return its content.

    Returns:
        str: The full text content of the specified file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed due to permissions.
        OSError: For other I/O related errors.
    """
    # Ask the user for the file path and strip surrounding whitespace.
    file_path = input("Enter the path to the file: ").strip()

    # Open the file in read mode with UTF‑8 encoding and read its content.
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------------- #
# Demo / test harness – only executed when the script is run directly.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        content = read_file_from_user()
        print("\n--- File Content Start ---")
        print(content)
        print("--- File Content End ---")
    except Exception as exc:
        # Print a user‑friendly error message.
        print(f"\nError reading file: {exc}")