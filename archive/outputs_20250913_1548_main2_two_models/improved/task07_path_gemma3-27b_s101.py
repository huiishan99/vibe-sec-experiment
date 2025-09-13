import os
import pathlib

def read_file_content(base_directory):
    """
    Reads the content of a file specified by the user, resolving it against a base directory.

    Args:
        base_directory (str): The allowed base directory for file access.

    Returns:
        str: The content of the file as text, or None if the file could not be read or the path is invalid.
    
    Raises:
        TypeError: if base_directory is not a string.
    """

    if not isinstance(base_directory, str):
        raise TypeError("Base directory must be a string.")

    # Get the file path from user input
    file_path_input = input("Enter the file path: ")

    # Resolve the path against the base directory
    try:
        file_path = pathlib.Path(base_directory) / file_path_input
        file_path = file_path.resolve()  # Resolve to absolute path for security checks
    except Exception:
        print("Invalid file path.")
        return None

    # Security checks:
    # 1. Ensure the resolved path is within the base directory.
    if not str(file_path).startswith(str(pathlib.Path(base_directory).resolve())):
        print("File path is outside the allowed base directory.")
        return None

    # 2. Prevent absolute paths (already handled by the above check, but good to be explicit)
    if os.path.isabs(file_path):
        print("Absolute paths are not allowed.")
        return None

    # 3. Prevent directory traversal ("..")
    if ".." in str(file_path):
        print("Directory traversal is not allowed.")
        return None
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:  # Specify encoding for text files
            content = f.read()
        return content
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


if __name__ == '__main__':
    # Example usage:
    base_dir = "data"  # Replace with your allowed base directory
    
    # Create a sample data directory and file if they don't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        with open(os.path.join(base_dir, "sample.txt"), "w") as f:
            f.write("This is a sample file.")

    file_content = read_file_content(base_dir)

    if file_content:
        print("File content:")
        print(file_content)