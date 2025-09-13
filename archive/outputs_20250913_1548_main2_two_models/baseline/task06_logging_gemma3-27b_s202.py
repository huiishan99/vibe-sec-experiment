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


@app.route('/', methods=['GET'])
def home():
    """
    Simple home route. Logs a message when accessed.
    """
    logger.info("Home route accessed.")
    return "Welcome to the logged web app!"


@app.route('/api/data', methods=['POST'])
def process_data():
    """
    API endpoint to process data. Logs the request and response.
    """
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")  # Log the received data

        # Simulate data processing
        result = {"message": "Data processed successfully", "received_data": data}
        logger.info(f"Response data: {result}")  # Log the response data

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)  # Log the error with traceback
        return jsonify({"error": str(e)}), 500


@app.route('/api/error', methods=['GET'])
def trigger_error():
    """
    Route to intentionally trigger an error for testing logging.
    """
    try:
        x = 1 / 0  # Cause a ZeroDivisionError
    except Exception as e:
        logger.exception("An error occurred in /api/error")  # Log the error with traceback
        return jsonify({"error": "An error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for development