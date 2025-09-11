#!/usr/bin/env python3
"""
api_client.py

A minimal, secure example of how to connect to an external API
using an API key that is loaded from environment variables.
The key is never hard‑coded in the source code.

Prerequisites
-------------
- Python 3.8+
- The `requests` library (install with `pip install requests`)

Environment
-----------
Set the API key in your environment.  A convenient way to do this
is to create a `.env` file in the same directory as this script
and load it with a tool such as `python-dotenv`.  Do **not** commit
the `.env` file to version control.

Sample `.env.example` (copy to `.env` and replace the placeholder):
------------------------------------------------------------------
# .env.example
# ------------------------------------------------------------------
# API_KEY=your_api_key_here
# ------------------------------------------------------------------
# Do NOT commit the .env file.  Keep it in your .gitignore.

Usage
-----
Run the script directly to see a simple API call in action:

    python api_client.py

"""

import os
import sys
import logging
from typing import Any, Dict

import requests

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# URL of the API endpoint you want to call.
API_ENDPOINT = "https://api.example.com/v1/data"

# Name of the environment variable that holds the API key.
API_KEY_ENV_VAR = "API_KEY"

# ----------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_api_key() -> str:
    """
    Retrieve the API key from environment variables.

    Raises:
        RuntimeError: If the API key is not set.
    """
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise RuntimeError(
            f"Missing required environment variable: {API_KEY_ENV_VAR}"
        )
    return api_key

def fetch_data(endpoint: str, api_key: str) -> Dict[str, Any]:
    """
    Make a GET request to the specified API endpoint using the provided
    API key for authentication.

    Args:
        endpoint: The full URL of the API endpoint.
        api_key:  The API key used for authentication.

    Returns:
        The JSON-decoded response from the API.

    Raises:
        requests.HTTPError: If the HTTP request returned an unsuccessful status code.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    logger.info("Sending request to %s", endpoint)
    response = requests.get(endpoint, headers=headers, timeout=10)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.error("API request failed: %s", exc)
        raise

    logger.info("Received successful response")
    return response.json()

# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------
def main() -> None:
    """
    Entry point of the script. Loads the API key, makes a request,
    and prints the result.
    """
    try:
        api_key = get_api_key()
    except RuntimeError as exc:
        logger.error(exc)
        sys.exit(1)

    try:
        data = fetch_data(API_ENDPOINT, api_key)
    except requests.HTTPError:
        sys.exit(1)

    # Pretty‑print the JSON response
    import json
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()