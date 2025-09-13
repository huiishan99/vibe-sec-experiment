import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_api(api_url, api_key):
    """
    Connects to an API using a provided API key.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key for authentication.

    Returns:
        dict: The JSON response from the API, or None if an error occurred.
    
    Raises:
        TypeError: If api_url or api_key are not strings.
        ValueError: If api_url or api_key are empty strings.
    """

    # Input validation: Check data types and ensure strings are not empty
    if not isinstance(api_url, str):
        raise TypeError("api_url must be a string.")
    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string.")
    if not api_url:
        raise ValueError("api_url cannot be an empty string.")
    if not api_key:
        raise ValueError("api_key cannot be an empty string.")

    headers = {
        'Authorization': f'Bearer {api_key}'  # Use Bearer token authentication - common practice
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except ValueError as e:  # Handle JSON decoding errors
        logging.error(f"Failed to decode JSON: {e}")
        return None


def main():
    """
    Main function to demonstrate API connection.
    """
    # Load API key from environment variable
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    if not api_url or not api_key:
        logging.error("API_URL and API_KEY environment variables must be set.")
        return

    try:
        data = connect_to_api(api_url, api_key)

        if data:
            logging.info("API response:")
            logging.info(data)
        else:
            logging.error("Failed to retrieve data from the API.")

    except (TypeError, ValueError) as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()