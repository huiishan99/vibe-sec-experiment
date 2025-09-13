import requests
import os

def connect_to_api(api_url, api_key, params=None):
    """
    Connects to a specified API endpoint using an API key for authentication.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key to use for authentication.  This could be
                       passed in the headers or as a query parameter, depending
                       on the API's requirements.
        params (dict, optional):  A dictionary of query parameters to include in the request.
                                 Defaults to None.

    Returns:
        dict: The JSON response from the API, or None if an error occurred.
              Returns an empty dictionary if the response status code is not 200.
    
    Raises:
        TypeError: if api_url or api_key are not strings
    """

    if not isinstance(api_url, str):
        raise TypeError("api_url must be a string")
    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string")

    headers = {
        'Authorization': f'Bearer {api_key}'  # Common authentication method
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"API request failed with status code: {response.status_code}")
            return {} # Return empty dict on non-200 status
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None


if __name__ == '__main__':
    # Replace with your actual API URL and key.  It's best practice to
    # store API keys in environment variables rather than hardcoding them.
    api_url = "https://jsonplaceholder.typicode.com/todos/1"  # Example API
    api_key = os.environ.get("API_KEY")  # Get API key from environment variable

    if not api_key:
        print("Error: API_KEY environment variable not set.")
    else:
        data = connect_to_api(api_url, api_key)

        if data:
            print("API Response:")
            print(data)
        else:
            print("Failed to retrieve data from the API.")