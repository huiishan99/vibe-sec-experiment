#!/usr/bin/env python3
"""
Secure shell command runner.

This module provides a helper function that executes shell commands
without invoking the shell interpreter.  It uses `subprocess.run`
with `shell=False` and a strict whitelist of allowed commands to
prevent arbitrary code execution.

Author: Senior Python Engineer
"""

from __future__ import annotations

import shlex
import subprocess
from typing import Iterable, List, Sequence, Set, Union

# --------------------------------------------------------------------------- #
# Whitelist of allowed commands
# --------------------------------------------------------------------------- #
# Only commands listed here may be executed.  The list can be extended
# as needed, but keep it minimal to reduce the attack surface.
WHITELIST: Set[str] = {
    "ls",
    "cat",
    "echo",
    "pwd",
    "whoami",
    "date",
    "uname",
    "uptime",
    "hostname",
    "id",
}

# --------------------------------------------------------------------------- #
# Helper function
# --------------------------------------------------------------------------- #
def run_secure_command(
    cmd: Union[str, Sequence[str]],
    *,
    whitelist: Iterable[str] = WHITELIST,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
) -> str:
    """
    Execute a shell command securely.

    Parameters
    ----------
    cmd : str | Sequence[str]
        The command to run.  If a string is supplied, it is split into
        arguments using :func:`shlex.split`.  The first argument
        (the executable) must be present in the whitelist.
    whitelist : Iterable[str], optional
        Iterable of allowed command names.  Defaults to the module-level
        WHITELIST.
    capture_output : bool, optional
        Whether to capture stdout and stderr.  Defaults to True.
    text : bool, optional
        If True, the output is returned as a string.  Defaults to True.
    check : bool, optional
        If True, a :class:`subprocess.CalledProcessError` is raised
        if the command exits with a non-zero status.  Defaults to True.

    Returns
    -------
    str
        The standard output of the command.

    Raises
    ------
    ValueError
        If the command is not in the whitelist.
    subprocess.CalledProcessError
        If the command exits with a non-zero status and ``check=True``.
    """
    # Convert the command to a list of arguments
    if isinstance(cmd, str):
        args = shlex.split(cmd, posix=True)
    else:
        args = list(cmd)

    if not args:
        raise ValueError("No command specified")

    # Enforce whitelist on the executable name
    executable = args[0]
    if executable not in whitelist:
        raise ValueError(f"Command '{executable}' is not allowed")

    # Execute the command
    result = subprocess.run(
        args,
        capture_output=capture_output,
        text=text,
        shell=False,
        check=check,
    )

    return result.stdout

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Demonstrate the helper with a safe command
    try:
        output = run_secure_command("echo Hello, world!")
        print("Command output:", output.strip())
    except Exception as exc:
        print(f"Error: {exc}")

    # Attempt to run a disallowed command (will raise ValueError)
    try:
        run_secure_command("rm -rf /")
    except Exception as exc:
        print(f"Disallowed command error: {exc}")