#!/usr/bin/env python3
"""
Minimal utility that prompts the user for a file path, reads the file,
and returns its content.

The function `read_file_from_input` encapsulates the logic.  It uses
Python's built‑in `input()` to obtain the path, then opens the file
in text mode and reads its entire contents.  Basic error handling
is included to inform the user if the file cannot be found or opened.
"""

from pathlib import Path
from typing import Optional


def read_file_from_input() -> Optional[str]:
    """
    Prompt the user for a file path, read the file, and return its content.

    Returns:
        The file's content as a string if the file was read successfully.
        None if the file could not be opened.
    """
    # Ask the user for the file path
    file_path = input("Enter the path to the file you want to read: ").strip()

    # Resolve the path to an absolute Path object
    path = Path(file_path).expanduser().resolve()

    # Attempt to read the file
    try:
        content = path.read_text(encoding="utf-8")
        return content
    except FileNotFoundError:
        print(f"Error: The file '{path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied when accessing '{path}'.")
    except OSError as exc:
        print(f"Error: An unexpected error occurred while reading '{path}': {exc}")

    return None


if __name__ == "__main__":
    # Example usage: read a file and print its contents
    file_content = read_file_from_input()
    if file_content is not None:
        print("\n--- File Content Start ---")
        print(file_content)
        print("--- File Content End ---")