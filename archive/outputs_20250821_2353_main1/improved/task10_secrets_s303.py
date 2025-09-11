"""
api_client.py
==============

A minimal, secure example of how to call an external API that requires an
authentication key.  The key is loaded from an environment variable so that
secrets are never hard‑coded in the source code.

Key features
------------
* Uses :pypi:`python-dotenv` to load a local ``.env`` file during development.
* Reads the key from the environment variable ``API_KEY``.
* Makes a GET request to a placeholder API endpoint.
* Handles common errors (missing key, network problems, non‑200 responses).
* Uses HTTPS and a timeout to avoid hanging requests.
* Does **not** log or print the key.

Dependencies
------------
* requests
* python-dotenv

Install them with:

    pip install requests python-dotenv

Usage
-----
1. Create a file named ``.env`` in the same directory with the following
   content (replace ``YOUR_API_KEY`` with your real key):

        API_KEY=YOUR_API_KEY

2. Run the script:

        python api_client.py

The script will print the JSON response from the API or an error message.

Sample .env.example
-------------------
Below is a sample ``.env.example`` file that you can copy to ``.env`` and
replace the placeholder with your actual key.

    # .env.example
    # Copy this file to .env and replace the placeholder with your API key.
    API_KEY=YOUR_API_KEY
"""

import os
import sys
import logging
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Load environment variables from a .env file if present.
# This is safe because .env is ignored by version control.
load_dotenv()

# Configure logging.  In production you might want to adjust the level or
# destination (e.g., to a file or external logging service).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# API endpoint – replace with the real endpoint you need to call.
API_URL = "https://api.example.com/v1/data"

# Timeout for the HTTP request (seconds).  Adjust as appropriate.
REQUEST_TIMEOUT = 10

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Returns:
        The API key string.

    Raises:
        RuntimeError: If the API_KEY environment variable is missing.
    """
    key = os.getenv("API_KEY")
    if not key:
        raise RuntimeError(
            "Missing required environment variable 'API_KEY'. "
            "Please set it in your environment or in a .env file."
        )
    return key

def build_headers(api_key: str) -> Dict[str, str]:
    """
    Construct HTTP headers for the API request.

    Args:
        api_key: The authentication key.

    Returns:
        A dictionary of HTTP headers.
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

def fetch_data() -> Dict[str, Any]:
    """
    Call the external API and return the parsed JSON response.

    Returns:
        The JSON payload as a Python dictionary.

    Raises:
        RuntimeError: For network errors or non‑200 responses.
    """
    api_key = get_api_key()
    headers = build_headers(api_key)

    try:
        logging.info("Sending request to %s", API_URL)
        response = requests.get(API_URL, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Network connection error: {exc}") from exc
    except requests.exceptions.HTTPError as exc:
        # Do not expose the raw response body if it contains sensitive data.
        raise RuntimeError(
            f"API returned error {response.status_code}: {response.reason}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        # Catch-all for any other request-related errors.
        raise RuntimeError(f"Unexpected error during request: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Failed to parse JSON response.") from exc

    logging.info("Successfully retrieved data from API.")
    return data

# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Main function that fetches data from the API and prints it.
    """
    try:
        data = fetch_data()
        # Pretty‑print the JSON response.
        print("API response:")
        print(data)
    except RuntimeError as exc:
        logging.error("Error: %s", exc)
        sys.exit(1)

if __name__ == "__main__":
    main()