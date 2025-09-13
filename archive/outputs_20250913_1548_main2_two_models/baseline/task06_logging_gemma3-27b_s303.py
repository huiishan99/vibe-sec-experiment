import logging
import os
from flask import Flask, request, jsonify

# Configure logging
# Use environment variables for configuration if available, otherwise use defaults
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')  # Default to INFO
LOG_FILE = os.environ.get('LOG_FILE', 'app.log') # Default to app.log

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='a'  # Append to the log file
)

logger = logging.getLogger(__name__)  # Get a logger for the current module

app = Flask(__name__)

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    """
    Handles GET and POST requests to the /api/data endpoint.
    Logs the request method, path, and any request data.
    Returns a JSON response.
    """
    logger.info(f"Received {request.method} request to {request.path}")

    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Request data: {data}") # Log the request data at debug level
            # Process the data (replace with your actual logic)
            result = {'message': 'Data received and processed', 'data': data}
            logger.info(f"Successfully processed request. Result: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True) # Log the exception with traceback
            return jsonify({'error': str(e)}), 500
    else: # GET request
        logger.warning("GET request received.  No data processing performed.")
        return jsonify({'message': 'GET request received'})

@app.route('/health')
def health_check():
    """
    A simple health check endpoint.  Logs a message indicating the check.
    """
    logger.info("Health check endpoint accessed.")
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Run the app
    app.run(debug=True) # Set debug=False for production