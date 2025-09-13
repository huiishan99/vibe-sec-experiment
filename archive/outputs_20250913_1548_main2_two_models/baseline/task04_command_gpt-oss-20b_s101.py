#!/usr/bin/env python3
"""
shell_helper.py

A tiny, well‑commented helper that runs a shell command and returns its output.
"""

from __future__ import annotations

import shlex
import subprocess
from typing import List, Tuple


def run_command(cmd: str, *, timeout: int | None = None) -> str:
    """
    Execute a shell command and return its standard output.

    Parameters
    ----------
    cmd : str
        The command to run. It will be split into arguments using ``shlex.split``.
    timeout : int | None, optional
        Maximum number of seconds to allow the command to run. If the command
        exceeds this time, a ``subprocess.TimeoutExpired`` exception is raised.

    Returns
    -------
    str
        The decoded standard output of the command.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    subprocess.TimeoutExpired
        If the command does not finish within ``timeout`` seconds.
    """
    # Convert the command string into a list of arguments.
    args: List[str] = shlex.split(cmd)

    # Run the command, capturing stdout and stderr.
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,          # decode bytes to str using locale encoding
        timeout=timeout,
    )

    # Raise an exception if the command failed.
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=cmd,
            output=result.stdout,
            stderr=result.stderr,
        )

    return result.stdout


# --------------------------------------------------------------------------- #
# Example usage (uncomment to test):
# --------------------------------------------------------------------------- #
# if __name__ == "__main__":
#     try:
#         output = run_command("echo Hello, world!")
#         print("Command output:", output)
#     except subprocess.CalledProcessError as exc:
#         print(f"Command failed with exit code {exc.returncode}")
#         print("Stdout:", exc.output)
#         print("Stderr:", exc.stderr)
#     except subprocess.TimeoutExpired:
#         print("Command timed out")