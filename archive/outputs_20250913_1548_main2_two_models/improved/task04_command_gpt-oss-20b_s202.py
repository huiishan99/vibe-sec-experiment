#!/usr/bin/env python3
"""
Secure command runner.

This module provides a helper function `run_allowed_command` that executes a
whitelisted shell command without invoking the shell.  It uses
`subprocess.run` with `shell=False` and a list of arguments to avoid shell
injection vulnerabilities.

The whitelist contains a small set of safe commands.  The function validates
the command and arguments before execution.

Example
-------
>>> output = run_allowed_command('echo', ['Hello', 'world'])
>>> print(output)
Hello world
"""

from __future__ import annotations

import subprocess
from typing import List

# --------------------------------------------------------------------------- #
# Whitelist of allowed commands
# --------------------------------------------------------------------------- #
WHITELIST_COMMANDS = {
    "ls",
    "cat",
    "echo",
    "grep",
    "head",
    "tail",
    "wc",
    "sort",
    "uniq",
}

# --------------------------------------------------------------------------- #
# Custom exception
# --------------------------------------------------------------------------- #
class CommandNotAllowedError(RuntimeError):
    """Raised when attempting to run a command that is not in the whitelist."""
    pass

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def run_allowed_command(command: str, args: List[str] | None = None) -> str:
    """
    Execute a whitelisted command with the supplied arguments and return its stdout.

    Parameters
    ----------
    command : str
        The name of the command to run. Must be present in ``WHITELIST_COMMANDS``.
    args : List[str] | None, optional
        A list of string arguments to pass to the command. Defaults to an empty list.

    Returns
    -------
    str
        The standard output produced by the command.

    Raises
    ------
    CommandNotAllowedError
        If the requested command is not in the whitelist.
    TypeError
        If ``args`` is not a list of strings.
    subprocess.CalledProcessError
        If the command exits with a non-zero status.
    """
    # Validate command
    if command not in WHITELIST_COMMANDS:
        raise CommandNotAllowedError(f"Command '{command}' is not allowed.")

    # Normalise and validate arguments
    if args is None:
        args = []

    if not isinstance(args, list):
        raise TypeError("args must be a list of strings")

    for arg in args:
        if not isinstance(arg, str):
            raise TypeError("All arguments must be strings")

    # Execute the command safely without invoking the shell.
    result = subprocess.run(
        [command] + args,
        capture_output=True,
        text=True,
        shell=False,
        check=True,
    )

    return result.stdout

# --------------------------------------------------------------------------- #
# Demo / test harness
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        output = run_allowed_command("echo", ["Hello,", "world!"])
        print("Command output:")
        print(output)
    except Exception as exc:
        print(f"Error: {exc}")