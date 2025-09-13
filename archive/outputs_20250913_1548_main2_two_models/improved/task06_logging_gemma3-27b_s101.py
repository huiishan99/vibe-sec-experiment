import logging
import os
from logging.handlers import RotatingFileHandler
import secrets  # For generating random secrets if needed

# Configure logging
LOG_FILE = 'app.log'
LOG_LEVEL = logging.INFO
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Create a rotating file handler
handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_LOG_FILE_SIZE,
    backupCount=BACKUP_COUNT,
    encoding='utf-8'  # Specify encoding for proper character handling
)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def redact_secret(text):
    """
    Redacts sensitive information (tokens, passwords) from a string.
    This is a basic example and should be adapted based on the specific
    secrets you need to protect.  More robust methods (e.g., regular expressions,
    secret detection libraries) may be necessary for production.
    """
    if not isinstance(text, str):
        return text  # Handle non-string inputs gracefully

    # Replace potential tokens/passwords with "[REDACTED]"
    redacted_text = text.replace("token=", "[REDACTED]")
    redacted_text = redacted_text.replace("password=", "[REDACTED]")
    redacted_text = redacted_text.replace("api_key=", "[REDACTED]")  # Add more as needed
    return redacted_text


def example_function(user_id, api_token, password):
    """
    An example function that demonstrates logging with redaction.
    """
    try:
        # Simulate some operation
        if user_id < 0:
            raise ValueError("User ID must be positive")

        # Log the request, redacting sensitive information
        log_message = f"User {user_id} requested data. Token: {api_token}, Password: {password}"
        redacted_message = redact_secret(log_message)
        logger.info(redacted_message)

        # Perform some operation
        result = user_id * 2
        logger.debug(f"Operation successful. Result: {result}")  # Log debug info
        return result

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return None


def generate_secret():
    """
    Generates a random secret token.  Use this to create secrets,
    but *never* log the generated secret directly.
    """
    return secrets.token_hex(16)  # Generates a 32-character hex token


if __name__ == '__main__':
    # Example usage
    user_id = 123
    api_token = generate_secret()
    password = "secure_password"  # In a real app, never hardcode passwords!

    result = example_function(user_id, api_token, password)

    if result is not None:
        print(f"Result: {result}")

    # Test error handling
    example_function(-1, api_token, password)