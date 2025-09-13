import bcrypt
import os
import json

def register_user(username, password, filepath="users.json"):
    """
    Registers a new user by hashing the password with bcrypt and storing
    the username and hashed password in a JSON file.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        filepath (str, optional): The path to the JSON file where user data
                                   will be stored. Defaults to "users.json".

    Returns:
        bool: True if registration was successful, False otherwise.
    
    Raises:
        ValueError: If the password is too short.
    """

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")

    # Generate a per-user salt
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt with the generated salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Load existing users from the file (if it exists)
    try:
        with open(filepath, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    except json.JSONDecodeError:
        print("Error decoding users.json. File may be corrupted. Overwriting.")
        users = {} #reset to avoid issues

    # Check if the username already exists
    if username in users:
        print("Username already exists.")
        return False

    # Store the username and hashed password in the dictionary
    users[username] = {
        'hashed_password': hashed_password.decode('utf-8'), #store as string for json
        'salt': salt.decode('utf-8') #store salt for verification
    }

    # Write the updated user data back to the file
    try:
        with open(filepath, 'w') as f:
            json.dump(users, f, indent=4)  # Use indent for readability
        return True
    except IOError:
        print("Error writing to file.")
        return False


def verify_password(username, password, filepath="users.json"):
    """
    Verifies a password against a stored hash.

    Args:
        username (str): The username to verify.
        password (str): The password to verify.
        filepath (str, optional): The path to the JSON file. Defaults to "users.json".

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    try:
        with open(filepath, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print("User file not found.")
        return False
    except json.JSONDecodeError:
        print("Error decoding users.json. File may be corrupted.")
        return False

    if username not in users:
        print("Username not found.")
        return False

    user_data = users[username]
    hashed_password = user_data['hashed_password'].encode('utf-8')
    salt = user_data['salt'].encode('utf-8')

    # Hash the provided password with the stored salt
    hashed_attempt = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Compare the hashed attempt with the stored hash
    return hashed_attempt == hashed_password


if __name__ == '__main__':
    # Example Usage
    try:
        if register_user("testuser", "SecurePassword123"):
            print("User registered successfully.")
        else:
            print("User registration failed.")

        if verify_password("testuser", "SecurePassword123"):
            print("Password verified successfully.")
        else:
            print("Password verification failed.")
    except ValueError as e:
        print(f"Error: {e}")