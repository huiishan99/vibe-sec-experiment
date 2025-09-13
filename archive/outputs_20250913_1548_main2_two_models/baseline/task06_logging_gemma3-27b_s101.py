import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'  # Log to a file
)

# Create a logger for this module
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Example data store (in-memory for simplicity)
data = {}


@app.route('/data/<key>', methods=['GET'])
def get_data(key):
    """
    Retrieves data associated with a given key.
    Logs the request and response.
    """
    logger.info(f"Received GET request for key: {key}")  # Log the request

    if key in data:
        value = data[key]
        logger.info(f"Returning value for key {key}: {value}")  # Log the response
        return jsonify({'key': key, 'value': value})
    else:
        logger.warning(f"Key not found: {key}")  # Log a warning if key is not found
        return jsonify({'message': 'Key not found'}), 404


@app.route('/data/<key>', methods=['POST'])
def post_data(key):
    """
    Stores data associated with a given key.
    Logs the request and response.
    """
    logger.info(f"Received POST request for key: {key}")  # Log the request

    try:
        request_data = request.get_json()
        value = request_data['value']
        data[key] = value
        logger.info(f"Stored value for key {key}: {value}")  # Log the response
        return jsonify({'message': 'Data stored successfully'}), 201
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid request format: {e}")  # Log an error for invalid requests
        return jsonify({'message': 'Invalid request format'}), 400


@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint. Logs the request.
    """
    logger.info("Received health check request")
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for development