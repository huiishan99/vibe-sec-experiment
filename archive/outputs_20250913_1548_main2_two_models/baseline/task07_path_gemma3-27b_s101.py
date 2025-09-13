def read_file_content(file_path):
    """
    Reads the content of a file specified by the given file path.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The content of the file as a string, or None if the file 
             cannot be opened or read.  Also returns None if the input
             is not a string.
    """

    if not isinstance(file_path, str):
        print("Error: File path must be a string.")
        return None

    try:
        with open(file_path, 'r') as f:  # Open the file in read mode ('r')
            content = f.read()  # Read the entire content of the file
        return content
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None
    except IOError:  # Handles other potential input/output errors
        print(f"Error: Could not read file at path: {file_path}")
        return None


if __name__ == '__main__':
    """
    Example usage:  Gets file path from user input and prints the content.
    """
    file_path = input("Enter the file path: ")
    file_content = read_file_content(file_path)

    if file_content:
        print("File content:")
        print(file_content)