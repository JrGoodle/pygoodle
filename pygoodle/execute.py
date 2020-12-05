"""Subprocess execution utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import subprocess
from pathlib import Path
from subprocess import CompletedProcess, STDOUT, PIPE
from typing import List, Union

from .console import CONSOLE


def run_command(command: Union[str, List[str]], cwd: Path = Path.home(),
                print_output: bool = True, check: bool = True, stdout=PIPE, stderr=STDOUT) -> CompletedProcess:
    stdout = stdout
    stderr = stderr
    if print_output:
        CONSOLE.stdout(f"[default bold]> {command}[/default bold]")
        stdout = None
        stderr = None

    if isinstance(command, list):
        cmd = ' '.join(command)
    else:
        cmd = command

    completed_process = subprocess.run(cmd, cwd=cwd, shell=True, stdout=stdout, stderr=stderr, text=True)

    if check and completed_process.returncode != 0:
        raise Exception(f'Command failed with exit code {completed_process.returncode}')

    return completed_process
