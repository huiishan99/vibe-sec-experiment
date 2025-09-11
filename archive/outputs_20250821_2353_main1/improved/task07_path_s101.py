#!/usr/bin/env python3
"""
Secure file reader.

This module defines a single function `read_user_file()` that:
* Prompts the user for a file path.
* Validates the path to ensure it is relative to a predefined base directory.
* Rejects absolute paths and any use of '..' to prevent directory traversal.
* Reads the file as UTF‑8 text and returns its contents.

The function raises descriptive exceptions on error, which can be caught
by the caller.  The module also contains a small demo in the `__main__`
section.
"""

from __future__ import annotations

import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Base directory that is allowed to contain user‑supplied files.
# Adjust this path as needed for your environment.
BASE_DIR: Path = Path(__file__).parent / "allowed_files"

# Ensure the base directory exists at import time.
# If it does not exist, create it to avoid errors later.
BASE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _is_path_safe(user_path: Path) -> None:
    """
    Validate that the supplied path is safe.

    Raises:
        ValueError: If the path is absolute or contains '..'.
    """
    if user_path.is_absolute():
        raise ValueError("Absolute paths are not allowed.")
    if ".." in user_path.parts:
        raise ValueError("Path traversal ('..') is not allowed.")


def _resolve_path(user_path: Path) -> Path:
    """
    Resolve the user path relative to BASE_DIR and ensure it stays within it.

    Returns:
        Path: The resolved absolute path.

    Raises:
        ValueError: If the resolved path is outside BASE_DIR.
    """
    # Resolve relative to BASE_DIR without following symlinks.
    resolved = (BASE_DIR / user_path).resolve(strict=False)

    # Python 3.9+ provides Path.is_relative_to; for older versions use commonpath.
    try:
        if not resolved.is_relative_to(BASE_DIR):
            raise ValueError("Resolved path is outside the allowed base directory.")
    except AttributeError:
        # Fallback for Python < 3.9
        if Path.commonpath([resolved, BASE_DIR]) != BASE_DIR:
            raise ValueError("Resolved path is outside the allowed base directory.")

    return resolved


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def read_user_file() -> str:
    """
    Prompt the user for a file path, validate it, and return its text content.

    The function enforces the following security constraints:
    * The path must be relative (no leading '/' or drive letters).
    * The path must not contain '..' components.
    * The resolved path must reside within BASE_DIR.
    * The file must exist and be a regular file.
    * The file is read as UTF‑8 text; decoding errors are replaced.

    Returns:
        str: The file's text content.

    Raises:
        ValueError: If the path is invalid or outside the allowed directory.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permissions.
    """
    # Prompt the user for a relative file path.
    user_input = input("Enter the relative path of the file to read: ").strip()
    if not user_input:
        raise ValueError("No path provided.")

    user_path = Path(user_input)

    # Validate the path components.
    _is_path_safe(user_path)

    # Resolve the path and ensure it stays within BASE_DIR.
    full_path = _resolve_path(user_path)

    # Ensure the target is an existing regular file.
    if not full_path.is_file():
        raise FileNotFoundError(f"File not found: {full_path}")

    # Read and return the file content as UTF‑8 text.
    try:
        return full_path.read_text(encoding="utf-8", errors="replace")
    except PermissionError as exc:
        raise PermissionError(f"Permission denied when reading {full_path}") from exc


# --------------------------------------------------------------------------- #
# Demo / entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    try:
        content = read_user_file()
        print("\n--- File Content Start ---")
        print(content)
        print("--- File Content End ---")
    except Exception as exc:
        # Print a user‑friendly error message and exit with non‑zero status.
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)