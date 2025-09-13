import pickle
import io
import logging
import flask
from flask import request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = flask.Flask(__name__)

@app.route('/load_object', methods=['POST'])
def load_object():
    """
    Receives a binary payload containing a pickled Python object, 
    unpickles it, and returns a JSON representation of the object.

    Security Considerations:
    - Unpickling data from untrusted sources is inherently dangerous.  
      It can lead to arbitrary code execution.  This service should 
      only be used with trusted data sources.  Consider using a more 
      secure serialization format like JSON or Protocol Buffers if 
      dealing with untrusted input.
    - Input validation is minimal in this example.  In a production 
      environment, you should add more robust validation to prevent 
      malformed or excessively large payloads.

    Returns:
        JSON: A JSON representation of the unpickled object.
              Returns an error message if unpickling fails or if the 
              request content type is incorrect.
    """
    try:
        # Check content type
        if request.content_type != 'application/octet-stream':
            logging.warning(f"Invalid content type: {request.content_type}. Expected application/octet-stream")
            return jsonify({'error': 'Invalid content type. Expected application/octet-stream'}), 400

        # Read the binary payload from the request
        binary_data = request.get_data()

        # Use io.BytesIO to treat the binary data as a file-like object
        byte_stream = io.BytesIO(binary_data)

        # Load the Python object using pickle
        try:
            unpickled_object = pickle.load(byte_stream)
        except pickle.UnpicklingError as e:
            logging.error(f"Unpickling error: {e}")
            return jsonify({'error': f'Unpickling error: {e}'}), 500
        except Exception as e:
            logging.error(f"Unexpected error during unpickling: {e}")
            return jsonify({'error': f'Unexpected error: {e}'}), 500

        # Convert the object to a JSON-serializable format.  
        # This is a basic attempt and may need to be customized 
        # based on the type of objects being serialized.
        try:
            json_object = jsonify(unpickled_object)
        except TypeError as e:
            logging.error(f"Error converting object to JSON: {e}")
            return jsonify({'error': f'Error converting object to JSON: {e}'}), 500

        return json_object

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500


if __name__ == '__main__':
    # Start the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)