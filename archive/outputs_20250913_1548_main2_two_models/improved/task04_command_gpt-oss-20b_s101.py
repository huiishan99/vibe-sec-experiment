#!/usr/bin/env python3
"""
Secure shell command helper.

This module provides a single function, :func:`run_command`, that executes
external commands safely:

* Only commands listed in :data:`ALLOWED_COMMANDS` may be run.
* The command and its arguments are passed as a list to :func:`subprocess.run`
  with ``shell=False`` – no shell expansion or injection is possible.
* The function returns the command's standard output as a string.
* If the command fails (non‑zero exit status) a :class:`subprocess.CalledProcessError`
  is raised with the captured output for debugging.

The helper is intentionally minimal – it is meant to be imported and used
directly in scripts or applications that need to run a few trusted commands.
"""

from __future__ import annotations

import subprocess
from typing import Iterable, List, Optional

# --------------------------------------------------------------------------- #
# Whitelist of allowed commands
# --------------------------------------------------------------------------- #
# Only commands in this set may be executed.  Add or remove entries as your
# application requires.  The names are the executable names as they would
# appear on the system PATH.
ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "echo",
    "grep",
    "head",
    "tail",
    "wc",
    "sort",
    "uniq",
    "cut",
    "awk",
    "sed",
}

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def run_command(
    command: str,
    args: Optional[Iterable[str]] = None,
    *,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
) -> str:
    """
    Execute a whitelisted shell command and return its standard output.

    Parameters
    ----------
    command : str
        The executable name to run.  Must be present in :data:`ALLOWED_COMMANDS`.
    args : Iterable[str] | None, optional
        Additional command‑line arguments.  Each element is passed as a
        separate list item – no shell parsing occurs.
    cwd : str | None, optional
        Working directory for the command.  If ``None`` the current directory
        is used.
    env : dict | None, optional
        Environment variables for the subprocess.  If ``None`` the current
        environment is inherited.

    Returns
    -------
    str
        The command's standard output decoded as UTF‑8.

    Raises
    ------
    ValueError
        If ``command`` is not in :data:`ALLOWED_COMMANDS`.
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.  The exception contains
        the captured ``stdout`` and ``stderr`` for debugging.
    OSError
        If the executable cannot be found or is not executable.

    Notes
    -----
    * ``shell=False`` is used to avoid shell injection vulnerabilities.
    * ``capture_output=True`` and ``text=True`` capture the output as a
      string, simplifying the API.
    """
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Command '{command}' is not allowed.")

    # Build the argument list.  ``args`` may be ``None``.
    cmd_list: List[str] = [command]
    if args:
        cmd_list.extend(args)

    # Execute the command.
    result = subprocess.run(
        cmd_list,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        shell=False,
        check=True,  # Raises CalledProcessError on non‑zero exit
    )

    return result.stdout

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    # Simple command‑line interface for demonstration.
    # Usage: python run_helper.py <command> [args...]
    if len(sys.argv) < 2:
        print("Usage: python run_helper.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    cmd_args = sys.argv[2:]

    try:
        output = run_command(cmd, cmd_args)
        print(output, end="")  # ``output`` already contains a trailing newline
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}", file=sys.stderr)
        print("stdout:", e.stdout, file=sys.stderr)
        print("stderr:", e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
    except OSError as e:
        print(f"Execution error: {e}", file=sys.stderr)
        sys.exit(3)