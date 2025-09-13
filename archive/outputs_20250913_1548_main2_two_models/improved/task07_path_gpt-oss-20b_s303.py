#!/usr/bin/env python3
"""
Secure file reader.

This module defines a single function, `read_file_from_user_input`, that:
* Prompts the user for a file path.
* Ensures the path is relative to a predefined base directory.
* Rejects absolute paths and any attempt to traverse outside the base directory
  (e.g. via '..').
* Reads the file as UTF‑8 text and returns its contents.

The function raises descriptive exceptions for common error conditions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# The directory that is allowed to contain readable files.
# Adjust this path to the directory you want to expose.
BASE_DIR: Final[Path] = Path(__file__).parent / "allowed"

# Maximum file size (bytes) to read.  Prevents accidental memory exhaustion.
MAX_FILE_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MiB

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _validate_user_path(user_path: str) -> Path:
    """
    Validate the user‑supplied path.

    Raises:
        ValueError: If the path is absolute, contains '..', or resolves outside
                    the allowed base directory.
    Returns:
        Path: The resolved absolute path within BASE_DIR.
    """
    # Convert to Path object
    rel_path = Path(user_path)

    # Reject absolute paths
    if rel_path.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    # Reject any '..' components that could escape the base directory
    if ".." in rel_path.parts:
        raise ValueError("Path traversal ('..') is not allowed.")

    # Resolve the path relative to BASE_DIR
    resolved = (BASE_DIR / rel_path).resolve(strict=True)

    # Ensure the resolved path is still within BASE_DIR
    try:
        resolved.relative_to(BASE_DIR.resolve(strict=True))
    except ValueError:
        raise ValueError("Resolved path is outside the allowed base directory.")

    return resolved

def _read_text_file(file_path: Path) -> str:
    """
    Read a text file safely.

    Raises:
        OSError: If the file cannot be accessed.
        UnicodeDecodeError: If the file is not valid UTF‑8.
    Returns:
        str: The file's contents.
    """
    # Enforce size limit
    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise OSError(f"File is too large ({file_path.stat().st_size} bytes).")

    # Read the file as UTF‑8 text
    return file_path.read_text(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def read_file_from_user_input() -> str:
    """
    Prompt the user for a file path, validate it, and return the file's text.

    The function enforces that the file resides within BASE_DIR and is a
    readable UTF‑8 text file.

    Returns:
        str: The file's contents.

    Raises:
        ValueError: If the input path is invalid.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
        UnicodeDecodeError: If the file is not valid UTF‑8.
        OSError: For other I/O errors.
    """
    # Prompt the user
    user_input = input(f"Enter a file path relative to {BASE_DIR}:\n> ").strip()

    # Validate and resolve the path
    file_path = _validate_user_path(user_input)

    # Ensure it's a regular file
    if not file_path.is_file():
        raise FileNotFoundError(f"'{file_path}' is not a regular file.")

    # Read and return the file contents
    return _read_text_file(file_path)

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    try:
        content = read_file_from_user_input()
        print("\n--- File Contents ---")
        print(content)
    except Exception as exc:
        # Print a concise error message to stderr
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)