import subprocess
import shlex
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_shell_command(command, args=None, allowed_commands=None):
    """
    Runs a shell command with arguments and returns its output.

    Args:
        command (str): The command to execute.
        args (list, optional): A list of arguments for the command. Defaults to None.
        allowed_commands (list, optional): A whitelist of allowed commands.
                                           If provided, the command will only be executed if it's in the whitelist.
                                           Defaults to None (no whitelist).

    Returns:
        str: The standard output of the command.
        None: If the command is not allowed (if a whitelist is provided) or if an error occurs.

    Raises:
        TypeError: if command is not a string or args is not a list.

    Security Considerations:
        - Uses subprocess.run with shell=False to avoid shell injection vulnerabilities.
        - Accepts arguments as a list, preventing command injection through argument parsing.
        - Implements a whitelist of allowed commands to further restrict execution.
        - Handles potential errors during command execution.
    """

    if not isinstance(command, str):
        raise TypeError("Command must be a string.")
    if args is not None and not isinstance(args, list):
        raise TypeError("Args must be a list.")

    if allowed_commands is not None:
        if command not in allowed_commands:
            logging.warning(f"Command '{command}' not allowed.  Allowed commands are: {allowed_commands}")
            return None

    try:
        # Construct the full command as a list
        full_command = [command] + args

        # Execute the command using subprocess.run
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)

        # Return the standard output
        logging.info(f"Command '{command}' executed successfully.")
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command}' failed with error: {e}")
        logging.error(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error(f"Command '{command}' not found.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


if __name__ == '__main__':
    # Example Usage
    allowed_commands = ['ls', 'grep', 'cat']  # Whitelist of allowed commands

    # Run a safe command
    output = run_shell_command('ls', ['-l'], allowed_commands)
    if output:
        print("ls -l output:")
        print(output)

    # Run a command with arguments
    output = run_shell_command('grep', ['example', 'test.txt'], allowed_commands)
    if output:
        print("grep output:")
        print(output)

    # Attempt to run a disallowed command
    output = run_shell_command('rm', ['-rf', '/'], allowed_commands)  # This should be blocked
    if output is None:
        print("Disallowed command blocked as expected.")

    # Test error handling
    output = run_shell_command('nonexistent_command')
    if output is None:
        print("Nonexistent command handled correctly.")