#!/usr/bin/env python3
"""
Utility module to execute shell commands and capture their output.

The main function, `run_command`, runs a command in a subprocess,
captures its standard output (and optionally standard error),
and returns the output as a string.  It raises a
`subprocess.CalledProcessError` if the command exits with a non‑zero
status code.

Example usage:

    >>> out = run_command('echo hello')
    >>> print(out)
    hello
"""

import subprocess
from typing import List, Optional


def run_command(
    command: str,
    *,
    args: Optional[List[str]] = None,
    capture_stderr: bool = False,
    check: bool = True,
) -> str:
    """
    Execute a shell command and return its output.

    Parameters
    ----------
    command : str
        The base command to run (e.g., 'ls', 'git', 'python').
    args : list[str] | None, optional
        Additional arguments to pass to the command.
    capture_stderr : bool, optional
        If True, stderr will be captured and appended to stdout.
    check : bool, optional
        If True (default), raise a CalledProcessError on non‑zero exit.

    Returns
    -------
    str
        The decoded standard output (and optionally stderr).

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status and `check` is True.
    """
    # Build the full command list
    cmd = [command]
    if args:
        cmd.extend(args)

    # Run the command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check,
    )

    # Combine stdout and stderr if requested
    output = result.stdout
    if capture_stderr:
        output += result.stderr

    return output


# Simple self‑test when run as a script
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_command.py <command> [args...]")
        sys.exit(1)

    # The first argument is the command, the rest are its arguments
    cmd = sys.argv[1]
    cmd_args = sys.argv[2:]

    try:
        out = run_command(cmd, args=cmd_args, capture_stderr=True)
        print(out)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        print("Stdout:", exc.stdout)
        print("Stderr:", exc.stderr)
        sys.exit(exc.returncode)