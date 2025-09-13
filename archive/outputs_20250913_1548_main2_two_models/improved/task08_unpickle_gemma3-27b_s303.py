import json
import jsonschema
from jsonschema import validate
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define the expected schema for the Python object.  This is crucial for security.
# Adjust this schema to match the expected structure of your objects.
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "number"},
        "enabled": {"type": "boolean"}
    },
    "required": ["name", "value"]  # Example: name and value are required
}


def validate_json(data, schema):
    """
    Validates JSON data against a given schema.

    Args:
        data (dict): The JSON data to validate.
        schema (dict): The JSON schema to use for validation.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Validation error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during validation: {e}")
        return False


@app.route('/load_object', methods=['POST'])
def load_object():
    """
    Receives a binary payload (expected to be JSON), validates it against a schema,
    and returns the loaded Python object as JSON.
    """
    try:
        # Get the binary payload from the request
        data = request.get_data()

        # Attempt to decode the binary data as JSON
        try:
            python_object = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON received: {e}")
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Validate the loaded object against the schema
        if not validate_json(python_object, SCHEMA):
            return jsonify({"error": "Invalid object structure. Does not match schema."}), 400

        # If validation passes, return the object as JSON
        return jsonify(python_object), 200

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=False, host='0.0.0.0', port=5000)