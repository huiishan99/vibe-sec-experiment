"""
api_client.py
==============

This module demonstrates how to securely connect to an external API using a
secret key that is loaded from environment variables.  The key is **never**
hard‑coded in the source code, and the module includes minimal error handling
and best‑practice security measures.

--------------------------------------------------------------------
Sample .env.example
--------------------------------------------------------------------
# Copy this file to .env and replace the placeholder with your real key.
# Do NOT commit the real key to version control.

API_KEY=your_api_key_here
API_ENDPOINT=https://api.example.com/v1/resource
"""

import os
import sys
import logging
from typing import Any, Dict

import requests

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------
# Configure logging – do NOT log the API key or any sensitive data.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# --------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------
def load_env_var(name: str) -> str:
    """
    Retrieve an environment variable and raise an error if it is missing.

    Args:
        name: The name of the environment variable.

    Returns:
        The value of the environment variable.

    Raises:
        RuntimeError: If the variable is not set.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is missing.")
    return value


def get_api_key() -> str:
    """Return the API key from the environment."""
    return load_env_var("API_KEY")


def get_api_endpoint() -> str:
    """Return the API endpoint URL from the environment."""
    return load_env_var("API_ENDPOINT")


# --------------------------------------------------------------------
# API client
# --------------------------------------------------------------------
class APIClient:
    """
    A simple API client that uses a bearer token for authentication.
    """

    def __init__(self, key: str, endpoint: str) -> None:
        self.key = key
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.key}",
                "Accept": "application/json",
                "User-Agent": "api-client/1.0",
            }
        )

    def fetch_resource(self, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Fetch data from the API endpoint.

        Args:
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.RequestException: For network-related errors.
        """
        try:
            logging.info("Sending request to %s", self.endpoint)
            response = self.session.get(
                self.endpoint,
                params=params,
                timeout=10,  # seconds
            )
            response.raise_for_status()
            logging.info("Received successful response")
            return response.json()
        except requests.HTTPError as http_err:
            logging.error("HTTP error occurred: %s", http_err)
            raise
        except requests.RequestException as req_err:
            logging.error("Request exception: %s", req_err)
            raise


# --------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------
def main() -> None:
    """
    Example usage of the APIClient.
    """
    try:
        api_key = get_api_key()
        api_endpoint = get_api_endpoint()
        client = APIClient(api_key, api_endpoint)

        # Example: fetch data with optional query parameters
        data = client.fetch_resource(params={"limit": 10})
        logging.info("Data received: %s", data)

    except Exception as exc:
        logging.exception("An error occurred: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()