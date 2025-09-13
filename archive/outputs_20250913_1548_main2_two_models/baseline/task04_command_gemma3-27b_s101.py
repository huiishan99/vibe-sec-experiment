import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_shell_command(command: str, check: bool = True) -> str:
    """
    Runs a shell command and returns its output as a string.

    Args:
        command: The shell command to execute.
        check:  If True, raise a CalledProcessError if the command exits with a non-zero exit code.
                Defaults to True.

    Returns:
        The standard output of the command.

    Raises:
        subprocess.CalledProcessError: If the command fails (check=True) and returns a non-zero exit code.
        TypeError: If command is not a string.
    """

    if not isinstance(command, str):
        raise TypeError("Command must be a string.")

    try:
        # Execute the command using subprocess.run
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)

        # Log the command and its output
        logging.info(f"Running command: {command}")
        logging.debug(f"Command output: {result.stdout}")

        # Return the standard output
        return result.stdout

    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with error: {e}")
        raise  # Re-raise the exception to signal failure to the caller
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise # Re-raise unexpected exceptions



if __name__ == '__main__':
    # Example Usage
    try:
        output = run_shell_command("ls -l")
        print("ls -l output:")
        print(output)

        # Example with a failing command (uncomment to test)
        # output = run_shell_command("false") # This will raise a CalledProcessError

    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except TypeError as e:
        print(f"Type Error: {e}")