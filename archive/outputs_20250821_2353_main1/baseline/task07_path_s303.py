#!/usr/bin/env python3
"""
Utility to read a file path from user input and return its content.
"""

def read_file_from_user() -> str:
    """
    Prompt the user for a file path, read the file's content, and return it.

    Returns:
        The content of the file as a string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be accessed due to permissions.
    """
    path = input("Enter the path to the file: ").strip()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    try:
        content = read_file_from_user()
        print("File content:")
        print(content)
    except Exception as e:
        print(f"Error: {e}")