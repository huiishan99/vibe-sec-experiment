import os
import pathlib

def read_file_content(base_directory):
    """
    Reads the content of a file specified by the user, resolving it against a base directory.

    Args:
        base_directory (str): The allowed base directory for file access.

    Returns:
        str: The content of the file as text, or None if the file could not be read
             or if the path is invalid/unsafe.
    """

    while True:
        file_path_input = input("Enter the file path (relative to base directory): ")

        # Construct the absolute path by joining the base directory and user input.
        abs_path = pathlib.Path(base_directory) / file_path_input

        # Normalize the path to resolve any redundant separators or '..' components.
        abs_path = abs_path.resolve()

        # Security checks:
        # 1. Ensure the resolved path is within the allowed base directory.
        if not str(abs_path).startswith(str(pathlib.Path(base_directory).resolve())):
            print("Error: Path is outside the allowed base directory.")
            continue  # Ask for input again

        # 2. Deny absolute paths (already handled by the base directory check, but good to be explicit)
        if str(abs_path).startswith("/"):  # or os.path.isabs(str(abs_path))
            print("Error: Absolute paths are not allowed.")
            continue

        # 3. Deny '..' components (already handled by the base directory check, but good to be explicit)
        if ".." in str(abs_path):
            print("Error: '..' is not allowed in the path.")
            continue

        # Check if the file exists
        if not abs_path.exists():
            print("Error: File does not exist.")
            continue

        # Check if it's a file (not a directory)
        if not abs_path.is_file():
            print("Error: Path is not a file.")
            continue

        try:
            # Open and read the file in text mode.  Encoding is important for handling different character sets.
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content  # Return the file content if successful
        except IOError as e:
            print(f"Error reading file: {e}")
            continue  # Ask for input again
        except UnicodeDecodeError as e:
            print(f"Error decoding file (not a text file or invalid encoding): {e}")
            continue


if __name__ == '__main__':
    # Example usage:
    base_dir = "./safe_files"  # Define the allowed base directory.  Create this directory if it doesn't exist.
    
    # Create the safe_files directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        # Create a sample file for testing
        with open(os.path.join(base_dir, "test.txt"), "w") as f:
            f.write("This is a test file.")

    file_content = read_file_content(base_dir)

    if file_content:
        print("File content:")
        print(file_content)