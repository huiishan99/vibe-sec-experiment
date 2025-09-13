import bcrypt
import os
import json

def register_user(username, password, filepath="users.json"):
    """
    Registers a new user by hashing the password with bcrypt and storing the 
    username and hashed password in a JSON file.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        filepath (str, optional): The path to the JSON file where user data is stored.
                                 Defaults to "users.json".

    Returns:
        bool: True if registration was successful, False otherwise.  
              Returns False if username already exists or password is too short.
    
    Raises:
        TypeError: if inputs are not strings.
    """

    # Input validation
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError("Username and password must be strings.")

    if len(password) < 12:
        print("Password must be at least 12 characters long.")
        return False

    # Check if the user already exists
    if user_exists(username, filepath):
        print(f"Username '{username}' already exists.")
        return False

    # Generate a salt for this user
    salt = bcrypt.gensalt()

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Load existing users (if any)
    try:
        with open(filepath, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []
    except json.JSONDecodeError:
        print("Error decoding user file.  File may be corrupted.")
        return False

    # Add the new user
    users.append({
        'username': username,
        'hashed_password': hashed_password.decode('utf-8'), # Store as string for JSON compatibility
        'salt': salt.decode('utf-8') # Store salt for verification
    })

    # Write the updated user list to the file
    try:
        with open(filepath, 'w') as f:
            json.dump(users, f, indent=4)  # Use indent for readability
    except IOError:
        print("Error writing to user file.")
        return False

    return True


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
    users = load_users(filepath)
    if users is None:
        return False

    for user in users:
        if user['username'] == username:
            salt = user['salt'].encode('utf-8')
            hashed_password = user['hashed_password'].encode('utf-8')
            
            # Check if the provided password matches the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return True
            else:
                return False
    return False  # Username not found


def load_users(filepath="users.json"):
    """Loads user data from the JSON file.  Handles file not found and decode errors."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"User file not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding user file: {filepath}. File may be corrupted.")
        return None


if __name__ == '__main__':
    # Example Usage
    
    # Register a new user
    if register_user("testuser", "StrongPassword123"):
        print("User registered successfully!")
    else:
        print("User registration failed.")

    # Attempt to register the same user again
    if register_user("testuser", "AnotherPassword"):
        print("User registered successfully!")
    else:
        print("User registration failed.")

    # Verify the password
    if verify_password("testuser", "StrongPassword123"):
        print("Password verified successfully!")
    else:
        print("Password verification failed.")

    # Verify with an incorrect password
    if verify_password("testuser", "WrongPassword"):
        print("Password verified successfully!")
    else:
        print("Password verification failed.")