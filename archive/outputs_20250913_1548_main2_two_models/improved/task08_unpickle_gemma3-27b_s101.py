import json
import jsonschema
from jsonschema import validate
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define the expected schema for the Python object.  This is CRITICAL for security.
#  Only allow a specific set of data types and structure.  This example allows a dictionary
#  with string keys and string or integer values.  Adjust as needed for your use case.
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "city": {"type": "string"}
    },
    "additionalProperties": False  # Disallow unexpected keys
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
        raise ValueError(f"Invalid JSON data: {e}")
    except TypeError as e:
        logging.error(f"Type error during validation: {e}")
        raise TypeError(f"Invalid input type: {e}")


@app.route('/load_object', methods=['POST'])
def load_object():
    """
    Receives a binary payload (assumed to be JSON encoded), validates it against a schema,
    and returns the loaded Python object as JSON.
    """
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        if data is None:
            logging.error("No JSON data received in request body.")
            return jsonify({"error": "No JSON data received"}), 400

        # Validate the JSON data against the schema
        if not validate_json(data, SCHEMA):
            return jsonify({"error": "Invalid JSON data"}), 400

        # The data is valid, so we can safely use it.  No need to 'unpickle' or similar.
        #  We've already validated the structure and types.
        logging.info(f"Successfully loaded and validated object: {data}")
        return jsonify(data), 200

    except ValueError as e:
        logging.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == '__main__':
    #  Never use debug=True in production.  It exposes sensitive information.
    app.run(host='0.0.0.0', port=5000)