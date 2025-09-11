#!/usr/bin/env python3
"""
Secure command runner.

This module provides a helper function `run_command` that executes a shell
command using `subprocess.run` with `shell=False` to avoid shell injection.
Only commands that are explicitly whitelisted are allowed.

Example
-------
>>> stdout, stderr, rc = run_command('echo', ['Hello, world!'])
>>> print(stdout.strip())
Hello, world!
"""

from __future__ import annotations

import subprocess
from typing import List, Tuple, Set


class DisallowedCommandError(RuntimeError):
    """Raised when attempting to run a command that is not in the whitelist."""
    pass


# --------------------------------------------------------------------------- #
# Whitelist of safe commands
# --------------------------------------------------------------------------- #
# The set contains the names of commands that are permitted to run.
# Add or remove commands using `add_to_whitelist` / `remove_from_whitelist`.
WHITELIST: Set[str] = {
    'echo',
    'ls',
    'cat',
    'grep',
    'head',
    'tail',
    'date',
    'whoami',
    'pwd',
    'uname',
    'env',
    'printf',
}


def run_command(command: str, args: List[str] | None = None) -> Tuple[str, str, int]:
    """
    Execute a whitelisted command with the given arguments.

    Parameters
    ----------
    command : str
        The name of the command to run (e.g., 'echo').
    args : list[str], optional
        A list of arguments to pass to the command. Defaults to an empty list.

    Returns
    -------
    tuple[str, str, int]
        stdout, stderr, and the return code of the process.

    Raises
    ------
    DisallowedCommandError
        If the command is not in the whitelist.
    """
    if args is None:
        args = []

    # --------------------------------------------------------------------- #
    # Security check: ensure the command is allowed
    # --------------------------------------------------------------------- #
    if command not in WHITELIST:
        raise DisallowedCommandError(f"Command '{command}' is not allowed.")

    # --------------------------------------------------------------------- #
    # Build the argument list for subprocess.run
    # --------------------------------------------------------------------- #
    cmd_list = [command] + args

    # --------------------------------------------------------------------- #
    # Execute the command safely
    # --------------------------------------------------------------------- #
    result = subprocess.run(
        cmd_list,
        capture_output=True,  # capture stdout and stderr
        text=True,            # return strings instead of bytes
        shell=False,          # do not invoke the shell
        check=False,          # do not raise on non-zero exit
    )

    return result.stdout, result.stderr, result.returncode


# --------------------------------------------------------------------------- #
# Helper functions to modify the whitelist
# --------------------------------------------------------------------------- #
def add_to_whitelist(command: str) -> None:
    """Add a command to the whitelist."""
    WHITELIST.add(command)


def remove_from_whitelist(command: str) -> None:
    """Remove a command from the whitelist."""
    WHITELIST.discard(command)


# --------------------------------------------------------------------------- #
# Demo / test harness
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Simple demo: run an allowed command
    try:
        out, err, rc = run_command('echo', ['Hello, secure world!'])
        print("STDOUT:", out.strip())
        print("STDERR:", err.strip())
        print("Return code:", rc)
    except DisallowedCommandError as e:
        print(f"Error: {e}")
    # Attempt to run a disallowed command
    try:
        run_command('rm', ['-rf', '/'])
    except DisallowedCommandError as e:
        print(f"Disallowed command caught as expected: {e}")
```