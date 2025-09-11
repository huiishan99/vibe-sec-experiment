# cmd_helper.py
"""
Utility to run shell commands and capture their output.

The :func:`run_command` function executes a command, waits for it to finish,
and returns the decoded standard output.  It raises a
:class:`subprocess.CalledProcessError` if the command exits with a non‑zero
status, and a :class:`subprocess.TimeoutExpired` if a timeout is supplied
and the command runs too long.

Typical usage:

>>> from cmd_helper import run_command
>>> out = run_command(['echo', 'hello'])
>>> print(out.strip())
hello
"""

from __future__ import annotations

import subprocess
from typing import List, Union

__all__ = ["run_command"]


def run_command(
    command: Union[str, List[str]],
    *,
    timeout: int | None = None,
    capture_stderr: bool = False,
) -> str:
    """
    Execute a shell command and return its stdout.

    Parameters
    ----------
    command : str | list[str]
        The command to run.  If a string, it is executed through the shell.
        If a list, it is passed directly to :func:`subprocess.run` without a
        shell.
    timeout : int | None, optional
        Maximum time in seconds to allow the command to run.  If omitted,
        the command may run indefinitely.
    capture_stderr : bool, default False
        If ``True``, ``stderr`` is merged into ``stdout`` so that the
        returned string contains both streams.

    Returns
    -------
    str
        The decoded standard output of the command.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    subprocess.TimeoutExpired
        If the command exceeds the specified timeout.
    """
    # Decide whether to use a shell based on the type of ``command``.
    if isinstance(command, str):
        shell = True
        args = command
    else:
        shell = False
        args = command

    # Run the command.
    result = subprocess.run(
        args,
        shell=shell,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
        stderr=subprocess.STDOUT if capture_stderr else None,
    )

    return result.stdout


if __name__ == "__main__":
    # Simple demo when the module is executed directly.
    try:
        output = run_command(["echo", "Hello, world!"])
        print("Command output:", output.strip())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
    except subprocess.TimeoutExpired:
        print("Command timed out")