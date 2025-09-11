#!/usr/bin/env python3
"""
A tiny helper module that runs a shell command and returns its output.

The :func:`run_command` function is intentionally minimal – it
executes the command, captures its standard output, and raises a
``subprocess.CalledProcessError`` if the command exits with a non‑zero
status.  It is suitable for quick scripts or unit tests where you
need the output of a command without having to write boilerplate
``subprocess`` code each time.

Example
-------
>>> from run_command import run_command
>>> run_command('echo hello')
'hello\n'
"""

from __future__ import annotations

import shlex
import subprocess
from typing import Iterable, List, Optional


def run_command(
    cmd: str | Iterable[str],
    *,
    timeout: Optional[float] = None,
    capture_stderr: bool = False,
) -> str:
    """
    Execute a shell command and return its standard output.

    Parameters
    ----------
    cmd : str | Iterable[str]
        The command to run.  If a string is supplied it is split using
        :func:`shlex.split` so that quoting rules are respected.
        If an iterable (e.g. a list) is supplied it is used verbatim.
    timeout : float, optional
        Maximum number of seconds to allow the command to run.  If the
        command exceeds this time a :class:`subprocess.TimeoutExpired`
        exception is raised.
    capture_stderr : bool, default False
        If ``True`` the command's standard error is captured and
        returned together with standard output.  When ``False`` the
        command's stderr is inherited from the parent process.

    Returns
    -------
    str
        The command's standard output decoded as UTF‑8.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    subprocess.TimeoutExpired
        If the command runs longer than ``timeout`` seconds.
    """
    # Convert the command to a list of arguments if it was supplied as a string.
    if isinstance(cmd, str):
        args: List[str] = shlex.split(cmd)
    else:
        args = list(cmd)

    # Configure the subprocess call.
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,  # decode bytes to str using locale encoding (UTF‑8 on most systems)
        timeout=timeout,
        check=True,  # raise CalledProcessError on non‑zero exit
        stderr=subprocess.PIPE if capture_stderr else None,
    )

    # If stderr was captured, prepend it to the output for clarity.
    output = result.stdout
    if capture_stderr and result.stderr:
        output = f"{result.stderr}\n{output}"
    return output


# --------------------------------------------------------------------------- #
# If this file is executed directly, run a simple demo.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_command.py <command>", file=sys.stderr)
        sys.exit(1)

    try:
        out = run_command(sys.argv[1:])
        print(out, end="")  # output already contains a trailing newline
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
    except subprocess.TimeoutExpired:
        print("Command timed out", file=sys.stderr)
        sys.exit(1)