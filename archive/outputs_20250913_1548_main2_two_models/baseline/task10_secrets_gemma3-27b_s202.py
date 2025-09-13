import requests
import os

def connect_to_api(api_url, api_key, params=None):
    """
    Connects to an API endpoint using a provided API key and optional parameters.

    Args:
        api_url (str): The URL of the API endpoint.
        api_key (str): The API key for authentication.
        params (dict, optional): A dictionary of query parameters to include in the request. 
                                 Defaults to None.

    Returns:
        dict: The JSON response from the API, or None if the request failed.
              Returns an empty dictionary if the response is not valid JSON.
    
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

        try:
            return response.json()  # Attempt to parse JSON response
        except ValueError:
            print("Warning: Response is not valid JSON.")
            return {} # Return empty dict if JSON parsing fails

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return None


if __name__ == '__main__':
    # Replace with your actual API URL and key.  Consider using environment variables
    # for sensitive information like API keys.
    api_url = "https://jsonplaceholder.typicode.com/todos/1"  # Example public API
    api_key = "your_api_key"  # Replace with your actual API key

    # Example usage with parameters
    params = {'param1': 'value1', 'param2': 'value2'}
    
    data = connect_to_api(api_url, api_key, params)

    if data:
        print("API Response:")
        print(data)
    else:
        print("Failed to retrieve data from the API.")