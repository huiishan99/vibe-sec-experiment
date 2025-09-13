import os
import pathlib

def read_file_content(base_directory):
    """
    Reads the content of a file specified by user input, 
    resolving the path relative to a base directory.

    Args:
        base_directory (str): The allowed base directory for file access.

    Returns:
        str: The content of the file as text, or None if the file 
             could not be read or the path is invalid.  Returns an empty
             string if the file exists but is empty.

    Raises:
        TypeError: if base_directory is not a string.
    """

    if not isinstance(base_directory, str):
        raise TypeError("Base directory must be a string.")

    file_path_input = input("Enter the file path: ")

    # Validate input:  Prevent absolute paths and directory traversal attacks.
    if os.path.isabs(file_path_input) or '..' in file_path_input:
        print("Invalid file path.  Relative paths only, no absolute paths or '..'.")
        return None

    # Resolve the path relative to the base directory.
    file_path = pathlib.Path(base_directory) / file_path_input
    file_path = file_path.resolve()  # Resolve to an absolute path for validation

    # Double check that the resolved path is still within the base directory.
    if not str(file_path).startswith(str(pathlib.Path(base_directory).resolve())):
        print("Invalid file path. Path is outside the allowed base directory.")
        return None

    # Check if the file exists
    if not file_path.exists():
        print("File does not exist.")
        return None

    try:
        # Open and read the file in text mode.
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except IOError as e:
        print(f"Error reading file: {e}")
        return None


if __name__ == '__main__':
    # Example usage:
    base_dir = "data"  # Replace with your allowed base directory.
    
    # Create a dummy data directory and file for testing
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    with open(os.path.join(base_dir, "test.txt"), "w") as f:
        f.write("This is a test file.")

    file_content = read_file_content(base_dir)

    if file_content is not None:
        print("File content:")
        print(file_content)