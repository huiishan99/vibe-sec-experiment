#!/usr/bin/env python3
"""
Utility to read a file whose path is supplied by the user.

The function `read_file_from_input` prompts the user for a file path,
reads the file's contents, and returns them as a string.
If the file cannot be found or opened, a FileNotFoundError is raised.
"""

from __future__ import annotations
from typing import Optional


def read_file_from_input() -> str:
    """
    Prompt the user for a file path, read the file, and return its contents.

    Returns:
        str: The entire content of the file.

    Raises:
        FileNotFoundError: If the specified file does not exist or cannot be opened.
    """
    # Ask the user for the file path
    file_path = input("Enter the path to the file: ").strip()

    # Open the file and read its contents
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Example usage (uncomment to run directly)
# if __name__ == "__main__":
#     try:
#         content = read_file_from_input()
#         print("\n--- File Content Start ---")
#         print(content)
#         print("--- File Content End ---")
#     except FileNotFoundError as e:
#         print(f"Error: {e}")