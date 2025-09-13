def read_file_content(file_path):
    """
    Reads the content of a file specified by the given path.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: The content of the file as a string, or None if the file 
             could not be read (e.g., file not found, permission error).
    """
    try:
        with open(file_path, 'r') as f:  # Open the file in read mode ('r')
            content = f.read()  # Read the entire content of the file
            return content
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read file: {file_path}")
        return None
    except Exception as e:  # Catch any other potential errors
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == '__main__':
    # Get the file path from the user
    file_path = input("Enter the path to the file: ")

    # Read the file content
    file_content = read_file_content(file_path)

    # Print the content if it was successfully read
    if file_content:
        print("File Content:")
        print(file_content)