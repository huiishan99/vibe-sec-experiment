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
        The standard output of the command.  Returns an empty string if an error occurs and check is False.

    Raises:
        subprocess.CalledProcessError: If the command fails and check is True.
        TypeError: If command is not a string.
    """

    if not isinstance(command, str):
        raise TypeError("Command must be a string.")

    try:
        # Use subprocess.run for more control and better error handling
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        logging.info(f"Command '{command}' executed successfully.")
        return result.stdout.strip()  # Return stdout and remove leading/trailing whitespace

    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command}' failed with error: {e}")
        raise  # Re-raise the exception if check is True
    except Exception as e:
        logging.error(f"An unexpected error occurred while running command '{command}': {e}")
        return ""  # Return empty string for other exceptions if check is False



if __name__ == '__main__':
    # Example usage
    try:
        output = run_shell_command("ls -l")
        print("ls -l output:")
        print(output)

        output = run_shell_command("echo 'Hello, world!'")
        print("\necho output:")
        print(output)

        # Example of a failing command (uncomment to test)
        # run_shell_command("nonexistent_command")

    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except TypeError as e:
        print(f"Type Error: {e}")