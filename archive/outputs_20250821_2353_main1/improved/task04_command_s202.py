#!/usr/bin/env python3
"""
Secure command runner.

This module provides a helper function `run_command` that executes a shell
command without invoking a shell interpreter.  The command is validated
against a whitelist of allowed executables to mitigate the risk of
arbitrary code execution.

Usage
-----
>>> output = run_command(['echo', 'Hello, world!'])
>>> print(output.strip())
Hello, world!
"""

from __future__ import annotations

import os
import subprocess
from typing import List, Dict, Optional

# --------------------------------------------------------------------------- #
# Whitelist of allowed command names.
# Only the base name of the executable is checked; the path is ignored.
# --------------------------------------------------------------------------- #
ALLOWED_COMMANDS: set[str] = {
    # Basic utilities
    "echo", "ls", "pwd", "cat", "head", "tail", "grep", "sort", "uniq", "wc",
    "date", "whoami", "id", "uname", "uptime", "df", "du", "ps", "free",
    "ping", "traceroute", "curl", "wget",

    # Version control & build tools
    "git", "hg", "svn", "make", "cmake", "mvn", "gradle", "npm", "yarn",
    "composer", "pip", "pip3", "pipenv", "poetry",

    # Programming language interpreters
    "python", "python3", "node", "ruby", "perl", "ruby", "php", "java",
    "javac", "bash", "sh", "zsh", "ksh", "csh", "tcsh",

    # Miscellaneous
    "docker", "kubectl", "helm", "aws", "gcloud", "az", "terraform",
    "ansible", "ansible-playbook",
}

# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def run_command(
    cmd: List[str],
    *,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
) -> str:
    """
    Execute a command securely and return its standard output.

    Parameters
    ----------
    cmd : list[str]
        The command and its arguments.  The first element must be the name
        (or path) of an executable that is present in :data:`ALLOWED_COMMANDS`.
    env : dict[str, str] | None, optional
        Environment variables for the subprocess.  If omitted, the current
        environment is inherited.
    cwd : str | None, optional
        Working directory for the subprocess.

    Returns
    -------
    str
        The decoded standard output of the command.

    Raises
    ------
    ValueError
        If the command is not in the whitelist or the command list is empty.
    subprocess.CalledProcessError
        If the command exits with a non‑zero status.
    FileNotFoundError
        If the executable cannot be found.
    """
    if not cmd:
        raise ValueError("Command list cannot be empty")

    # Resolve the base name of the executable to check against the whitelist.
    executable = os.path.basename(cmd[0])
    if executable not in ALLOWED_COMMANDS:
        raise ValueError(f"Command '{executable}' is not allowed")

    # Run the command without invoking a shell.
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        env=env,
        cwd=cwd,
        shell=False,  # Never use the shell – prevents shell injection.
    )
    return result.stdout

# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        out = run_command(["echo", "Hello, world!"])
        print(f"Command output: {out.strip()}")
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}")
```