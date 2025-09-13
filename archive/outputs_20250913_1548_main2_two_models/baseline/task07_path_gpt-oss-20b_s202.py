#!/usr/bin/env python3
"""
Utility to read a file whose path is supplied by the user.

The `read_file_from_user` function prompts the user for a file path,
attempts to read the file as text, and returns its contents.
If the file cannot be read, an error message is printed and `None`
is returned.
"""

from pathlib import Path
from typing import Optional


def read_file_from_user() -> Optional[str]:
    """
    Prompt the user for a file path, read the file, and return its content.

    Returns:
        The file's content as a string if successful, otherwise None.
    """
    # Ask the user for the file path
    file_path = input("Enter the path to the file you want to read: ").strip()

    # Resolve the path to an absolute Path object
    path = Path(file_path).expanduser().resolve()

    # Check that the path exists and is a file
    if not path.is_file():
        print(f"Error: '{path}' is not a valid file.")
        return None

    try:
        # Read and return the file's content
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        # Catch any I/O or decoding errors
        print(f"Failed to read '{path}': {exc}")
        return None


# Example usage
if __name__ == "__main__":
    content = read_file_from_user()
    if content is not None:
        print("\n--- File Content Start ---")
        print(content)
        print("--- File Content End ---")