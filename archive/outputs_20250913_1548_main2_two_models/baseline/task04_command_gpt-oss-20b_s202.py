#!/usr/bin/env python3
"""
A small helper module that runs a shell command and returns its output.

Usage:
    from run_cmd import run_command

    output = run_command("echo hello")
    print(output)  # prints "hello\n"
"""

import subprocess
import shlex
from typing import Tuple


def run_command(command: str, *, capture_stderr: bool = False) -> str:
    """
    Execute *command* in a subshell and return its standard output as a string.

    Parameters
    ----------
    command : str
        The shell command to execute. It can contain arguments and shell
        operators (e.g. pipes, redirects).  The command is passed to the
        underlying shell via ``subprocess.run`` with ``shell=True``.
    capture_stderr : bool, optional
        If ``True`` the command's standard error will be captured and
        appended to the returned output.  Defaults to ``False``.
        When ``False`` the command's stderr is inherited from the parent
        process (i.e. it will be printed to the console).

    Returns
    -------
    str
        The decoded standard output of the command.  If the command exits
        with a non‑zero status, a ``subprocess.CalledProcessError`` is
        raised.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    """
    # Build the subprocess arguments
    kwargs = {
        "shell": True,
        "text": True,          # return strings instead of bytes
        "check": True,         # raise CalledProcessError on non‑zero exit
    }

    if capture_stderr:
        kwargs["stderr"] = subprocess.STDOUT

    # Run the command
    result = subprocess.run(command, **kwargs)

    # result.stdout is already a string because of `text=True`
    return result.stdout


# Example usage (uncomment to test)
# if __name__ == "__main__":
#     print(run_command("echo 'Hello, world!'"))