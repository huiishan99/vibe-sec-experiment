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
    encoding='utf-8'  # Specify encoding for consistent handling of characters
)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def redact_secret(text):
    """
    Redacts sensitive information (tokens, passwords) from a string.
    This is a basic example and should be expanded for production use.
    """
    if not text:
        return ""

    # Simple redaction - replace potential tokens/passwords with "[REDACTED]"
    # This is a placeholder.  More sophisticated pattern matching or
    # a dedicated secrets detection library should be used in production.
    redacted_text = text.replace("token=", "[REDACTED]")
    redacted_text = redacted_text.replace("password=", "[REDACTED]")
    redacted_text = redacted_text.replace("api_key=", "[REDACTED]")
    return redacted_text


def log_request(request_data):
    """Logs request data, redacting sensitive information."""
    # Log the request data, but redact secrets
    redacted_data = redact_secret(str(request_data))
    logger.info(f"Received request: {redacted_data}")


def process_data(data):
    """Processes data and logs the process."""
    try:
        # Simulate some data processing
        result = data * 2
        logger.info(f"Processed data: {data} -> {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return None


def main():
    """Main function to demonstrate logging."""

    # Example request data (potentially containing secrets)
    request_data = {
        "user_id": 123,
        "api_key": "some_secret_api_key",
        "data": "some data",
        "token": "some_auth_token"
    }

    log_request(request_data)

    # Process some data
    data_to_process = 10
    result = process_data(data_to_process)

    if result is not None:
        logger.info(f"Final result: {result}")
    else:
        logger.warning("Data processing failed.")

    # Example of generating a random secret (for demonstration)
    # In a real application, store secrets securely (e.g., environment variables,
    # a secrets manager) and *never* log them.
    # random_secret = secrets.token_hex(16)
    # logger.info("Generated a random secret (DO NOT LOG IN PRODUCTION)")


if __name__ == "__main__":
    main()