#!/usr/bin/env python3
"""
Sample script that connects to a REST API using an API key stored in an
environment variable.  The key is never hard‑coded in the source code.

--------------------------------------------------------------------
# .env.example
# Copy this file to .env and replace the placeholder with your real key.
# Do NOT commit the .env file to version control.

API_KEY=your_api_key_here
API_BASE_URL=https://api.example.com/v1
--------------------------------------------------------------------
"""

import os
import sys
import logging
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------
# Load environment variables from a .env file if present.
load_dotenv()

# Retrieve the API key and base URL from the environment.
API_KEY: str | None = os.getenv("API_KEY")
API_BASE_URL: str | None = os.getenv("API_BASE_URL")

# Basic validation – exit if required variables are missing.
if not API_KEY:
    logging.error("Missing required environment variable: API_KEY")
    sys.exit(1)

if not API_BASE_URL:
    logging.error("Missing required environment variable: API_BASE_URL")
    sys.exit(1)

# --------------------------------------------------------------------
# Logging configuration
# --------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# --------------------------------------------------------------------
# API client
# --------------------------------------------------------------------
class APIClient:
    """
    Simple wrapper around requests to interact with the target API.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        # Use HTTPS by default; requests will raise an error if the URL is HTTP.
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "SecureAPIClient/1.0",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Internal helper to perform an HTTP request and return JSON data.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logging.error("Request failed: %s", exc)
            raise

        try:
            return response.json()
        except ValueError:
            logging.error("Response is not valid JSON: %s", response.text)
            raise

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Example GET request to fetch a resource by ID.
        """
        endpoint = f"resources/{resource_id}"
        logging.info("Fetching resource %s", resource_id)
        return self._request("GET", endpoint)

    def list_resources(self) -> Dict[str, Any]:
        """
        Example GET request to list resources.
        """
        endpoint = "resources"
        logging.info("Listing resources")
        return self._request("GET", endpoint)

# --------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------
def main() -> None:
    client = APIClient(API_BASE_URL, API_KEY)

    # Example usage – replace with real logic as needed.
    try:
        # List all resources
        resources = client.list_resources()
        logging.info("Resources: %s", resources)

        # Fetch a specific resource (replace '123' with a real ID)
        resource = client.get_resource("123")
        logging.info("Resource 123: %s", resource)

    except Exception as exc:
        logging.exception("An error occurred while interacting with the API: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()