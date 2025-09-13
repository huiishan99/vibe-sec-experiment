import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_shell_command(command, check=True):
    """
    Runs a shell command and returns its output.

    Args:
        command (str or list): The command to run.  Can be a string or a list of strings.
                               If a string, it will be split into a list using shell-like tokenization.
        check (bool, optional): If True, raise a CalledProcessError if the command exits with a non-zero exit code.
                                Defaults to True.

    Returns:
        str: The standard output of the command.

    Raises:
        subprocess.CalledProcessError: If the command fails (non-zero exit code) and check is True.
        TypeError: If command is not a string or list.
    """

    if not isinstance(command, (str, list)):
        raise TypeError("Command must be a string or a list of strings.")

    try:
        # Use subprocess.run for more control and error handling
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        logging.info(f"Command executed successfully: {command}")
        return result.stdout.strip()  # Return stdout and remove leading/trailing whitespace

    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}.  Return code: {e.returncode}.  Stderr: {e.stderr}")
        raise  # Re-raise the exception to signal failure to the caller
    except FileNotFoundError as e:
        logging.error(f"Command not found: {command}. Error: {e}")
        raise # Re-raise the exception
    except Exception as e:
        logging.error(f"An unexpected error occurred while running command: {command}. Error: {e}")
        raise # Re-raise the exception



if __name__ == '__main__':
    # Example Usage
    try:
        output = run_shell_command("ls -l")
        print("ls -l output:")
        print(output)

        output = run_shell_command(["echo", "Hello, world!"])
        print("\necho output:")
        print(output)

        # Example with a failing command (uncomment to test error handling)
        # run_shell_command("nonexistent_command")

    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except TypeError as e:
        print(f"Type Error: {e}")