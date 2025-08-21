#!/usr/bin/env python3
"""
A tiny helper that executes a shell command and returns its standard output.

The function uses :func:`subprocess.run` with ``shell=True`` so the caller can
pass a single string containing the command exactly as they would type it in a
terminal.  The output is returned as a decoded string (``text=True``).  If the
command fails (non‑zero exit status) a :class:`subprocess.CalledProcessError`
is raised, which contains the exit code and the captured output.

Example
-------
>>> from run_command import run_command
>>> run_command('echo hello')
'hello\\n'
"""

from __future__ import annotations

import subprocess
from typing import Final

__all__: Final = ["run_command"]


def run_command(command: str) -> str:
    """
    Execute *command* in a shell and return its standard output.

    Parameters
    ----------
    command : str
        The shell command to run.  It may contain arguments, pipes, etc.

    Returns
    -------
    str
        The command's standard output, decoded as UTF‑8.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    """
    # ``text=True`` ensures we get a string instead of bytes.
    # ``capture_output=True`` captures both stdout and stderr.
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=True,  # raise CalledProcessError on non‑zero exit
    )
    return result.stdout