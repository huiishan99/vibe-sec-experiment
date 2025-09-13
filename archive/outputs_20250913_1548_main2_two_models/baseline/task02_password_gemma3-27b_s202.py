import hashlib
import os

def register_user(username, password, filepath="users.txt"):
    """
    Registers a new user by storing a hashed password associated with the username
    in a file.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        filepath (str, optional): The path to the file where user data will be stored.
                                  Defaults to "users.txt".

    Returns:
        bool: True if registration was successful, False otherwise (e.g., username already exists).
    
    Raises:
        TypeError: if username or password are not strings
    """

    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError("Username and password must be strings.")

    # Hash the password for security.  Using SHA-256.
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Check if the user already exists.
    if user_exists(username, filepath):
        print(f"Username '{username}' already exists.")
        return False

    # Append the username and hashed password to the file.
    try:
        with open(filepath, "a") as f:
            f.write(f"{username}:{hashed_password}\n")
        print(f"User '{username}' registered successfully.")
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False


def user_exists(username, filepath="users.txt"):
    """
    Checks if a user with the given username already exists in the file.

    Args:
        username (str): The username to check.
        filepath (str, optional): The path to the user data file. Defaults to "users.txt".

    Returns:
        bool: True if the user exists, False otherwise.
    """
    try:
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith(username + ":"):
                    return True
        return False
    except FileNotFoundError:
        return False  # File doesn't exist, so user can't exist.
    except Exception as e:
        print(f"Error reading file: {e}")
        return False


if __name__ == '__main__':
    # Example Usage
    register_user("testuser", "P@sswOrd123")
    register_user("anotheruser", "securepassword")
    register_user("testuser", "newpassword") # Attempt to register existing user

    # Check if user exists
    print(f"Does testuser exist? {user_exists('testuser')}")
    print(f"Does nonexistinguser exist? {user_exists('nonexistinguser')}")