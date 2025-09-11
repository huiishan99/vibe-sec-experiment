#!/usr/bin/env python3
"""
Utility module for executing shell commands.

The :func:`run_command` helper runs a command in a subprocess and returns its
standard output as a string.  It is a thin wrapper around
:func:`subprocess.run` that handles common options such as text mode,
capturing output, and optional error checking.

Typical usage:

>>> output = run_command(['echo', 'Hello, world!'])
>>> print(output)
Hello, world!

"""

from __future__ import annotations

import subprocess
from typing import List, Optional, Union


def run_command(
    cmd: Union[str, List[str]],
    *,
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    env: Optional[dict] = None,
    cwd: Optional[str] = None,
) -> str:
    """
    Execute a shell command and return its standard output.

    Parameters
    ----------
    cmd : str | list[str]
        The command to run.  If a string is provided, it is executed through
        the shell (``shell=True``).  If a list is provided, it is passed
        directly to the subprocess without shell expansion.
    capture_output : bool, default True
        Whether to capture stdout and stderr.  If False, the command's
        output will be printed directly to the parent process's streams.
    text : bool, default True
        If True, the output is returned as a string (decoded using the
        system default encoding).  If False, bytes are returned.
    check : bool, default False
        If True, raise :class:`subprocess.CalledProcessError` if the
        command exits with a non‑zero status.
    env : dict | None, default None
        Environment variables for the new process.  If None, the current
        environment is used.
    cwd : str | None, default None
        Working directory for the command.  If None, the current directory
        is used.

    Returns
    -------
    str
        The command's standard output (decoded if ``text=True``).

    Raises
    ------
    subprocess.CalledProcessError
        If ``check=True`` and the command exits with a non‑zero status.
    """
    # Prepare the subprocess arguments
    if isinstance(cmd, str):
        # When a string is given, run it through the shell
        kwargs = {"shell": True}
    else:
        # When a list is given, avoid shell expansion
        kwargs = {"shell": False}

    # Common keyword arguments
    kwargs.update(
        {
            "capture_output": capture_output,
            "text": text,
            "env": env,
            "cwd": cwd,
        }
    )

    # Execute the command
    result = subprocess.run(cmd, **kwargs)

    # Optionally raise an exception on non‑zero exit status
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=cmd,
            output=result.stdout,
            stderr=result.stderr,
        )

    # Return the captured stdout (or an empty string if not captured)
    return result.stdout or ""


# If this module is executed directly, demonstrate a simple example.
if __name__ == "__main__":
    try:
        output = run_command(["python", "--version"], check=True)
        print(f"Command output: {output.strip()}")
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        print(f"stderr: {exc.stderr}")