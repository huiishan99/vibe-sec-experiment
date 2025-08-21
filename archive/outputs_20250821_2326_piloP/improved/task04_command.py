#!/usr/bin/env python3
"""
Secure command execution helper.

This module provides a single function `run_command` that executes a shell
command safely and returns its standard output.  It uses
`subprocess.run` with `shell=False` to avoid shell injection attacks.
Only commands that are explicitly whitelisted are allowed to run.

Author: Senior Python Engineer
"""

from __future__ import annotations

import subprocess
from typing import List

# --------------------------------------------------------------------------- #
# Whitelist of allowed commands
# --------------------------------------------------------------------------- #
# Only commands listed here can be executed.  The list can be extended
# by adding more safe utilities as needed.
ALLOWED_COMMANDS = {
    "ls",
    "echo",
    "cat",
    "grep",
    "head",
    "tail",
    "wc",
    "date",
    "whoami",
    "uptime",
}

# --------------------------------------------------------------------------- #
# Custom exception types
# --------------------------------------------------------------------------- #
class CommandNotAllowedError(RuntimeError):
    """Raised when an attempt is made to run a non‑whitelisted command."""
    pass


class CommandExecutionError(RuntimeError):
    """Raised when a whitelisted command fails during execution."""

    def __init__(self, command: List[str], returncode: int, output: str) -> None:
        self.command = command
        self.returncode = returncode
        self.output = output
        super().__init__(
            f"Command '{' '.join(command)}' failed with return code {returncode}"
        )


# --------------------------------------------------------------------------- #
# Helper function
# --------------------------------------------------------------------------- #
def run_command(args: List[str]) -> str:
    """
    Execute a whitelisted command and return its standard output.

    Parameters
    ----------
    args : List[str]
        The command and its arguments as a list.  The first element must be
        the command name (e.g., ['ls', '-l']).

    Returns
    -------
    str
        The decoded standard output of the command.

    Raises
    ------
    CommandNotAllowedError
        If the command is not in the whitelist or contains a slash.
    CommandExecutionError
        If the command exits with a non‑zero status.
    ValueError
        If the argument list is empty or contains non‑string elements.
    """
    # Basic validation
    if not args:
        raise ValueError("Argument list must not be empty.")
    if not all(isinstance(arg, str) for arg in args):
        raise ValueError("All arguments must be strings.")

    command = args[0]

    # Reject commands that look like paths (contain '/')
    if "/" in command:
        raise CommandNotAllowedError(
            f"Command '{command}' contains a slash and is not allowed."
        )

    # Enforce whitelist
    if command not in ALLOWED_COMMANDS:
        raise CommandNotAllowedError(
            f"Command '{command}' is not in the whitelist of allowed commands."
        )

    # Execute the command safely
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        shell=False,  # Do not invoke the shell
    )

    if result.returncode != 0:
        raise CommandExecutionError(args, result.returncode, result.stdout + result.stderr)

    return result.stdout


# --------------------------------------------------------------------------- #
# Example usage (only runs when executed as a script)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Demonstrate a safe command
    try:
        output = run_command(["echo", "Hello, world!"])
        print("Command output:", output.strip())
    except Exception as exc:
        print(f"Error: {exc}")

    # Attempt to run a disallowed command (uncomment to test)
    # try:
    #     run_command(["rm", "-rf", "/"])
    # except Exception as exc:
    #     print(f"Error: {exc}")