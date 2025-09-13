import json
import jsonschema
from jsonschema import validate
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define the expected schema for the Python object.  This is crucial for security.
#  Adjust this schema to match the expected structure of your objects.
#  Be as specific as possible to prevent unexpected data from being loaded.
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "integer"},
        "enabled": {"type": "boolean"}
    },
    "required": ["name", "value"]  # Define required fields
}


def validate_json(data, schema):
    """
    Validates a JSON object against a given schema.

    Args:
        data (dict): The JSON data to validate.
        schema (dict): The JSON schema to validate against.

    Returns:
        bool: True if the data is valid, False otherwise.  Raises a ValueError if input is invalid.
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"JSON validation error: {e}")
        raise ValueError(f"Invalid JSON data: {e}")  # Raise exception for handling in the route
    except TypeError as e:
        logging.error(f"Invalid input type: {e}")
        raise TypeError(f"Invalid input type: {e}")


@app.route('/load_object', methods=['POST'])
def load_object():
    """
    Receives a binary payload (expected to be JSON), validates it against a schema,
    and returns the loaded object as JSON.
    """
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        # Validate the JSON data against the schema
        if not validate_json(data, SCHEMA):
            return jsonify({"error": "Invalid JSON data"}), 400

        # At this point, the data is validated and safe to use.
        # Process the validated data as needed.  For example, you could
        # create an instance of a class using the data.

        # Example:  Just return the validated data as JSON.
        logging.info(f"Successfully loaded and validated object: {data}")
        return jsonify(data), 200

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400
    except TypeError as e:
        logging.error(f"TypeError: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Disable debug mode in production