#!/usr/bin/env python3
"""
Secure shell command helper.

This module provides a single function, `run_command`, that executes a
whitelisted shell command with optional arguments and returns its
standard output.  It uses `subprocess.run` with `shell=False` to avoid
shell injection vulnerabilities and ensures that only approved
commands are allowed to run.

Author: Senior Python Engineer
"""

from __future__ import annotations

import subprocess
from typing import Iterable, List

# --------------------------------------------------------------------------- #
# Whitelist of allowed commands
# --------------------------------------------------------------------------- #
# Only commands listed here can be executed.  Add or remove entries as
# required by your application.  The names are the command names as they
# would appear on the command line (no paths or arguments).
WHITELIST: set[str] = {
    "ls",
    "echo",
    "cat",
    "grep",
    "head",
    "tail",
    "date",
    "whoami",
}

# --------------------------------------------------------------------------- #
# Helper function
# --------------------------------------------------------------------------- #
def run_command(command: str, *args: str) -> str:
    """
    Execute a whitelisted shell command and return its standard output.

    Parameters
    ----------
    command : str
        The name of the command to run.  Must be present in :data:`WHITELIST`.
    *args : str
        Optional positional arguments to pass to the command.

    Returns
    -------
    str
        The decoded standard output of the command.

    Raises
    ------
    ValueError
        If the requested command is not in the whitelist.
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    """
    # Validate the command against the whitelist
    if command not in WHITELIST:
        raise ValueError(f"Command '{command}' is not allowed.")

    # Build the argument list for subprocess.run
    cmd_list: List[str] = [command, *args]

    # Execute the command securely
    result = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,          # decode bytes to str using locale encoding
        shell=False,        # do not invoke the shell
        check=True,         # raise CalledProcessError on non‑zero exit
    )

    return result.stdout

# --------------------------------------------------------------------------- #
# Example usage / simple tests
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Successful command
    try:
        output = run_command("echo", "Hello, world!")
        print("echo output:", output.strip())
    except Exception as exc:
        print(f"Error running echo: {exc}")

    # Attempt to run a non‑whitelisted command
    try:
        run_command("rm", "-rf", "/")
    except ValueError as exc:
        print(f"Security check: {exc}")

    # Another whitelisted command
    try:
        output = run_command("date")
        print("date output:", output.strip())
    except Exception as exc:
        print(f"Error running date: {exc}")