def read_file_content(file_path):
    """
    Reads the content of a file specified by the given file path.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: The content of the file as a string.  Returns None if the file
             cannot be opened or read.  Handles file not found errors gracefully.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None  # Indicate failure
    except Exception as e:  # Catch other potential errors (e.g., permission issues)
        print(f"An error occurred: {e}")
        return None


if __name__ == '__main__':
    """
    Example usage:  Gets file path from user and prints the content.
    """
    file_path = input("Enter the file path: ")
    file_content = read_file_content(file_path)

    if file_content:
        print("File content:")
        print(file_content)