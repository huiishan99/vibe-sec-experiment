#!/usr/bin/env python3
"""
Minimal example of connecting to a third‑party API using a key that is
loaded from environment variables.

Secure coding practices demonstrated:
* Secrets are never hard‑coded in the source.
* The key is read from the environment (via a .env file or the real
  environment of the deployment system).
* The key is never logged or printed.
* Errors from the HTTP request are handled gracefully.
* The code is type‑annotated and documented for clarity.

Dependencies
------------
* python-dotenv  (pip install python-dotenv)
* requests       (pip install requests)

Usage
-----
1. Create a copy of the sample .env.example file below and fill in your
   actual API key:

   # .env.example
   # API_KEY=your_api_key_here

2. Rename the copy to `.env` in the same directory as this script.
3. Run the script:

   $ python3 api_client.py

"""

import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Load environment variables from a .env file (if present)
# --------------------------------------------------------------------------- #
load_dotenv()  # Loads variables from .env into os.environ

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
API_URL = "https://api.example.com/v1/resource"  # Replace with the real endpoint


def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Raises:
        RuntimeError: If the API key is not set.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError(
            "API_KEY is not set. Please set it in your environment or in a .env file."
        )
    return key


def call_api() -> Dict[str, Any]:
    """
    Make a GET request to the API endpoint using the API key for authentication.

    Returns:
        The JSON-decoded response from the API.

    Raises:
        requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        requests.RequestException: For network-related errors.
    """
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
    except requests.HTTPError as http_err:
        # Log the error without exposing the API key
        print(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
        raise
    except requests.RequestException as req_err:
        # Handles connection errors, timeouts, etc.
        print(f"Request error occurred: {req_err}")
        raise

    # Parse JSON response
    try:
        return response.json()
    except ValueError as json_err:
        print(f"Failed to decode JSON response: {json_err}")
        raise


def main() -> None:
    """
    Entry point of the script.
    """
    try:
        data = call_api()
        print("API response:")
        print(data)
    except Exception as exc:
        print(f"An error occurred while calling the API: {exc}")


if __name__ == "__main__":
    main()