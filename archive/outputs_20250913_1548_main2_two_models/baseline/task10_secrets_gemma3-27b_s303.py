import requests
import os

def connect_to_api(api_url, api_key, params=None):
    """
    Connects to a specified API endpoint using an API key for authentication.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key to use for authentication.
        params (dict, optional):  A dictionary of query parameters to include in the request.
                                  Defaults to None.

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
        raise ValueError("api_url cannot be an empty string")
    if not api_key:
        raise ValueError("api_key cannot be an empty string")
    

    headers = {
        'Authorization': f'Bearer {api_key}'  # Common authentication method
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()  # Parse JSON response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None  # Handle errors gracefully
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None


if __name__ == '__main__':
    # Replace with your actual API URL and key.  It's best practice to load
    # the API key from an environment variable for security.
    api_url = "https://jsonplaceholder.typicode.com/todos/1"  # Example public API
    api_key = os.environ.get("API_KEY")  # Get API key from environment variable
    
    if not api_key:
        print("API_KEY environment variable not set.  Please set it.")
    else:
        data = connect_to_api(api_url, api_key)

        if data:
            print("API Response:")
            print(data)
        else:
            print("Failed to connect to the API.")