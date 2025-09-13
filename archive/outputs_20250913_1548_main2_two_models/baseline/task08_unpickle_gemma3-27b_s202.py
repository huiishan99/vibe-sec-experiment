import pickle
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_object_from_binary(binary_payload: bytes):
    """
    Loads a Python object from a binary payload using pickle.

    Args:
        binary_payload: The binary data representing the pickled object.

    Returns:
        The loaded Python object, or None if an error occurs.
    
    Raises:
        TypeError: if input is not bytes
        pickle.UnpicklingError: if the payload is not a valid pickle
        Exception: For any other unexpected errors during unpickling.
    """

    if not isinstance(binary_payload, bytes):
        raise TypeError("Input must be bytes.")

    try:
        # Use io.BytesIO to treat the byte string as a file-like object
        with io.BytesIO(binary_payload) as buffer:
            # Load the object using pickle.load()
            loaded_object = pickle.load(buffer)
            logging.info("Object successfully loaded from binary payload.")
            return loaded_object
    except pickle.UnpicklingError as e:
        logging.error(f"Error unpickling object: {e}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}") # Log full traceback
        return None


if __name__ == '__main__':
    # Example Usage:

    # Create a sample object to pickle
    sample_data = {"name": "Alice", "age": 30, "city": "New York"}

    # Pickle the object into a byte string
    pickled_data = pickle.dumps(sample_data)

    # Load the object from the binary payload
    loaded_data = load_object_from_binary(pickled_data)

    if loaded_data:
        print("Loaded data:", loaded_data)

    # Example with invalid payload
    invalid_payload = b"This is not a valid pickle"
    loaded_invalid = load_object_from_binary(invalid_payload)
    if loaded_invalid is None:
        print("Invalid payload handled correctly.")

    # Example with incorrect input type
    try:
        load_object_from_binary("not bytes")
    except TypeError as e:
        print(f"TypeError handled: {e}")