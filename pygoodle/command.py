"""Subprocess command utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import os
import subprocess
from pathlib import Path
from subprocess import CompletedProcess, PIPE, STDOUT
from typing import List, Optional, Union

from .console import CONSOLE
from .format import Format


def run_command(command: Union[str, List[str]], cwd: Path = Path.home(),
                print_output: Optional[bool] = None, check: bool = True, env: Optional[dict] = None,
                stdout=PIPE, stderr=STDOUT) -> CompletedProcess:

    if print_output is None:
        print_output = CONSOLE.print_output

    if print_output:
        output = Format.default(f"> {command}")
        output = Format.bold(output)
        CONSOLE.stdout(output)
        stdout = None
        stderr = None

    if isinstance(command, list):
        cmd = ' '.join(command)
    else:
        cmd = command

    cmd_env = os.environ.copy()
    if env is not None:
        cmd_env.update(env)

    # TODO: Replace universal_newlines with text when Python 3.6 support is dropped
    completed_process = subprocess.run(cmd, cwd=cwd, env=cmd_env, shell=True, stdout=stdout,
                                       stderr=stderr, universal_newlines=True, check=check)
    return completed_process
