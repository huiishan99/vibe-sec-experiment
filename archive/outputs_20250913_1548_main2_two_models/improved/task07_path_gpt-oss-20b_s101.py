#!/usr/bin/env python3
"""
Secure file reader.

This module defines a single function, `read_user_file()`, that:
* Prompts the user for a file path.
* Ensures the path is relative, contains no '..' components, and is not absolute.
* Resolves the path against a predefined base directory.
* Verifies that the resolved path remains inside the base directory.
* Reads the file as UTF‑8 text and returns its contents.

The function raises a ValueError if any security check fails or if the file
cannot be read as text.  All exceptions are caught and reported to the user
without exposing stack traces or sensitive information.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# The directory that is allowed to contain user‑requested files.
# Adjust this path as needed for your application.
ALLOWED_BASE_DIR: Path = Path(__file__).parent / "allowed_files"

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _is_safe_path(user_path: Path) -> bool:
    """
    Validate that the user‑supplied path is safe.

    Rules:
    * Must not be absolute.
    * Must not contain any '..' components.
    * Must resolve to a location inside ALLOWED_BASE_DIR.
    """
    # Reject absolute paths
    if user_path.is_absolute():
        return False

    # Reject paths that contain '..'
    if ".." in user_path.parts:
        return False

    # Resolve the path relative to the base directory
    resolved = (ALLOWED_BASE_DIR / user_path).resolve()

    # Ensure the resolved path is still inside the allowed base directory
    try:
        # Python 3.9+ provides is_relative_to
        return resolved.is_relative_to(ALLOWED_BASE_DIR)
    except AttributeError:
        # Fallback for older Python versions
        return str(resolved).startswith(str(ALLOWED_BASE_DIR))

def _read_text_file(file_path: Path) -> str:
    """
    Read the file at *file_path* as UTF‑8 text.

    Raises:
        ValueError: If the file cannot be read or is not valid UTF‑8.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}") from None
    except PermissionError:
        raise ValueError(f"Permission denied: {file_path}") from None
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF‑8 text: {file_path}") from None
    except OSError as exc:
        raise ValueError(f"Error reading file {file_path}: {exc}") from None

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def read_user_file() -> str:
    """
    Prompt the user for a file path, validate it, and return its contents.

    Returns:
        The file's text content.

    Raises:
        ValueError: If the path is unsafe, the file does not exist, or cannot be read.
    """
    # Prompt the user for a relative file path
    user_input = input("Enter the relative path of the file to read: ").strip()
    user_path = Path(user_input)

    # Validate the path
    if not _is_safe_path(user_path):
        raise ValueError("Invalid or unsafe file path provided.")

    # Resolve the full path
    full_path = (ALLOWED_BASE_DIR / user_path).resolve()

    # Read and return the file content
    return _read_text_file(full_path)

# --------------------------------------------------------------------------- #
# Command‑line entry point
# --------------------------------------------------------------------------- #

def _main() -> None:
    """
    Simple command‑line interface for testing the secure file reader.
    """
    try:
        content = read_user_file()
        print("\n--- File Content Start ---")
        print(content)
        print("--- File Content End ---")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    _main()