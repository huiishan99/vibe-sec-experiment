#!/usr/bin/env python3
"""
Secure file reader.

This module defines a single function `read_user_file()` that:
1. Prompts the user for a file path.
2. Validates that the path is relative, contains no '..' components,
   and does not start with an absolute path.
3. Resolves the path against a predefined allowed base directory.
4. Ensures the resolved path is still inside the base directory.
5. Reads the file as UTF‑8 text (with errors replaced) and returns its
   content as a string.

The implementation follows secure coding practices:
- Uses pathlib for path manipulation.
- Rejects absolute paths and path traversal attempts.
- Checks that the resolved path is a regular file and within the
  allowed directory.
- Limits the maximum file size to prevent memory exhaustion.
"""

from __future__ import annotations

from pathlib import Path
import sys

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Directory that is allowed to contain readable files.
# Adjust this path as needed for your environment.
BASE_DIR: Path = Path(__file__).parent / "allowed_files"

# Maximum file size (bytes) that will be read. 10 MiB is a reasonable limit.
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MiB

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _validate_and_resolve(user_input: str) -> Path:
    """
    Validate the user-supplied path and resolve it against BASE_DIR.

    Parameters
    ----------
    user_input : str
        The raw path string entered by the user.

    Returns
    -------
    Path
        The absolute, resolved path that is guaranteed to be inside BASE_DIR.

    Raises
    ------
    ValueError
        If the path is absolute, contains '..', or resolves outside BASE_DIR.
    FileNotFoundError
        If the file does not exist.
    """
    # Convert to a Path object for easier manipulation.
    rel_path = Path(user_input)

    # Reject absolute paths.
    if rel_path.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    # Reject any '..' components to prevent directory traversal.
    if ".." in rel_path.parts:
        raise ValueError("Path traversal using '..' is not allowed.")

    # Resolve the path against the allowed base directory.
    # strict=True ensures that a FileNotFoundError is raised if the file
    # does not exist.
    resolved = (BASE_DIR / rel_path).resolve(strict=True)

    # Ensure the resolved path is still within BASE_DIR.
    try:
        resolved.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError("Resolved path is outside the allowed base directory.")

    # Ensure the resolved path is a regular file.
    if not resolved.is_file():
        raise ValueError("Resolved path is not a regular file.")

    return resolved

def _read_text_file(path: Path) -> str:
    """
    Read the file at `path` as UTF‑8 text.

    Parameters
    ----------
    path : Path
        The file to read.

    Returns
    -------
    str
        The file's content decoded as UTF‑8.  Any decoding errors are
        replaced with the Unicode replacement character.

    Raises
    ------
    OSError
        If the file cannot be read.
    """
    # Enforce a maximum file size to avoid memory exhaustion.
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the maximum allowed limit.")

    with path.open("r", encoding="utf-8", errors="replace") as f:
        return f.read()

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def read_user_file() -> str:
    """
    Prompt the user for a file path, validate it, and return its text content.

    Returns
    -------
    str
        The content of the requested file as a string.

    Raises
    ------
    ValueError
        If the user input is invalid or the file cannot be accessed.
    FileNotFoundError
        If the specified file does not exist.
    OSError
        For other I/O related errors.
    """
    # Prompt the user for a file path.
    user_input = input("Enter the relative path of the file to read: ").strip()

    # Validate and resolve the path.
    resolved_path = _validate_and_resolve(user_input)

    # Read and return the file content.
    return _read_text_file(resolved_path)

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    try:
        content = read_user_file()
        print("\n--- File Content Start ---\n")
        print(content)
        print("\n--- File Content End ---")
    except Exception as exc:
        # In a real application, consider logging the exception details.
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)