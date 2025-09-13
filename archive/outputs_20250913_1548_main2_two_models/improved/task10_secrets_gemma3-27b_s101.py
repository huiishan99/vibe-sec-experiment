import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_api_data(api_url, api_key, params=None):
    """
    Connects to an API using a key loaded from environment variables.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key.
        params (dict, optional):  Query parameters to include in the request. Defaults to None.

    Returns:
        dict: The JSON response from the API, or None if an error occurred.
    
    Raises:
        TypeError: if api_url or api_key are not strings
        ValueError: if api_url or api_key are empty strings
    """

    # Input validation
    if not isinstance(api_url, str):
        raise TypeError("api_url must be a string")
    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string")
    if not api_url:
        raise ValueError("api_url cannot be empty")
    if not api_key:
        raise ValueError("api_key cannot be empty")
    

    headers = {
        'Authorization': f'Bearer {api_key}'  # Use Bearer token authentication.  More secure than passing in URL.
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except ValueError as e: #Handles invalid JSON response
        logging.error(f"Invalid JSON response: {e}")
        return None


def main():
    """
    Main function to demonstrate API connection.
    """
    # Load API key from environment variable
    api_key = os.getenv("API_KEY")
    if not api_key:
        logging.error("API_KEY environment variable not set.")
        return

    api_url = "https://api.example.com/data"  # Replace with your API endpoint
    params = {"param1": "value1", "param2": "value2"} #Example parameters

    data = get_api_data(api_url, api_key, params)

    if data:
        logging.info("API data received:")
        logging.info(data)
    else:
        logging.error("Failed to retrieve API data.")


if __name__ == "__main__":
    main()