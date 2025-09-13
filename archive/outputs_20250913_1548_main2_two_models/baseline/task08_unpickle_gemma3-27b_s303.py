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
        The loaded Python object.  Returns None if loading fails.

    Raises:
        TypeError: if input is not bytes.
        pickle.UnpicklingError: if the payload is not a valid pickle.
        Exception: For any other unexpected errors during unpickling.
    """

    if not isinstance(binary_payload, bytes):
        raise TypeError("Input must be bytes.")

    try:
        # Use io.BytesIO to treat the byte string as a file-like object
        with io.BytesIO(binary_payload) as buffer:
            # Load the object using pickle.load
            loaded_object = pickle.load(buffer)
            logging.info("Object loaded successfully.")
            return loaded_object
    except pickle.UnpicklingError as e:
        logging.error(f"Error unpickling object: {e}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        return None


if __name__ == '__main__':
    # Example Usage:

    # Create a sample object to pickle
    sample_data = {"name": "Example", "value": 123}

    # Pickle the object
    pickled_data = pickle.dumps(sample_data)

    # Load the object from the pickled data
    loaded_data = load_object_from_binary(pickled_data)

    if loaded_data:
        print("Loaded data:", loaded_data)
        assert loaded_data == sample_data, "Loaded data does not match original data."

    # Test with invalid data
    invalid_data = b"This is not a valid pickle"
    loaded_invalid = load_object_from_binary(invalid_data)
    assert loaded_invalid is None, "Should return None for invalid data"

    # Test with invalid input type
    try:
        load_object_from_binary("not bytes")
    except TypeError as e:
        print(f"TypeError caught as expected: {e}")
    else:
        print("TypeError not raised for non-bytes input.")