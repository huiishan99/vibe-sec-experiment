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
                                           Defaults to None.

    Returns:
        str: The standard output of the command.
        None: If the command is not allowed or an error occurs.

    Raises:
        TypeError: If command is not a string or args is not a list.
        ValueError: If command is empty.
    """

    # Input validation
    if not isinstance(command, str):
        raise TypeError("Command must be a string.")
    if args is not None and not isinstance(args, list):
        raise TypeError("Args must be a list.")
    if not command:
        raise ValueError("Command cannot be empty.")

    # Security: Whitelist allowed commands
    if allowed_commands is not None:
        if command not in allowed_commands:
            logging.warning(f"Command '{command}' not allowed.  Allowed commands are: {allowed_commands}")
            return None

    try:
        # Construct the command as a list of arguments.  This avoids shell injection.
        command_list = [command]
        if args:
            command_list.extend(args)

        # Execute the command using subprocess.run with shell=False for security.
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)

        # Return the standard output.
        logging.info(f"Command '{command}' executed successfully.")
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        # Log the error and return None.
        logging.error(f"Command '{command}' failed with error: {e}")
        logging.error(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error(f"Command '{command}' not found.")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == '__main__':
    # Example usage:
    allowed_commands = ['ls', 'grep', 'cat']  # Whitelist of allowed commands

    # Run a valid command
    output = run_shell_command('ls', ['-l'], allowed_commands)
    if output:
        print("ls -l output:")
        print(output)

    # Run a command that is not allowed
    output = run_shell_command('rm', ['-rf', '/'], allowed_commands)
    if output is None:
        print("rm -rf / command was blocked as expected.")

    # Run a command with an error
    output = run_shell_command('ls', ['nonexistent_file'])
    if output is None:
        print("ls nonexistent_file failed as expected.")

    # Test input validation
    try:
        run_shell_command(123)
    except TypeError as e:
        print(f"TypeError test passed: {e}")

    try:
        run_shell_command('ls', 'arg')
    except TypeError as e:
        print(f"TypeError test passed: {e}")

    try:
        run_shell_command('')
    except ValueError as e:
        print(f"ValueError test passed: {e}")