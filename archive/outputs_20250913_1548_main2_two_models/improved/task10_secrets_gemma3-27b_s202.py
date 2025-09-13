import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_api_data(api_url, api_key):
    """
    Connects to an API using a key loaded from environment variables and retrieves data.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key for authentication.

    Returns:
        dict: The JSON response from the API, or None if an error occurred.
    
    Raises:
        TypeError: if api_url or api_key are not strings
        ValueError: if api_url or api_key are empty strings
    """

    # Input validation - crucial for security and robustness
    if not isinstance(api_url, str):
        raise TypeError("API URL must be a string.")
    if not isinstance(api_key, str):
        raise TypeError("API Key must be a string.")
    if not api_url:
        raise ValueError("API URL cannot be empty.")
    if not api_key:
        raise ValueError("API Key cannot be empty.")
    

    headers = {
        'Authorization': f'Bearer {api_key}'  # Use Bearer token for authentication - common practice
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except ValueError as e: #Handles invalid JSON responses
        logging.error(f"Invalid JSON response: {e}")
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

    # Call the API function
    data = get_api_data(api_url, api_key)

    if data:
        logging.info("API data retrieved successfully:")
        #print(data) #Be careful about printing sensitive data
        logging.info(f"Example data: {data.get('example_field', 'No example field')}") #Access specific fields safely
    else:
        logging.error("Failed to retrieve API data.")


if __name__ == "__main__":
    main()