"""unrar utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import fnmatch
import os
import shutil
from pathlib import Path
from typing import List, Optional

from .console import CONSOLE
from .execute import run_command


def list_subdirectories(path: Path, recursive: bool = False) -> List[Path]:
    if recursive:
        return [Path(info[0]) for info in os.walk(path)]
    else:
        paths = [Path(str(p)) for p in os.scandir(path)]
        return [f.path for f in paths if f.is_dir()]


def find_rar(directory: Path) -> Optional[Path]:
    files = os.listdir(directory)
    files = [directory / f for f in files if f.endswith('.rar')]
    if not files:
        return
    return files[0]


def make_dir(dir_path: Path) -> None:
    if dir_path.exists():
        return
    CONSOLE.stdout(f'Create directory {dir_path}')
    os.makedirs(dir_path)


def move(input_path: Path, output_path: Path) -> None:
    CONSOLE.stdout(f'Move {input_path} to {output_path}')
    shutil.move(str(input_path), str(output_path))


def remove_dir(dir_path: Path, print_output: bool = True) -> None:
    if print_output:
        CONSOLE.stdout(f'Remove dir {dir_path}')
    shutil.rmtree(str(dir_path))


def remove_file(file: Path, print_output: bool = True) -> None:
    if print_output:
        CONSOLE.stdout(f'Remove file {file}')
    os.remove(str(file))


def replace_path_prefix(path: Path, old_prefix: Path, new_prefix: Path):
    # assert path.is_absolute()
    # assert path.is_relative_to(old_prefix)
    relative_path = path.relative_to(old_prefix)
    return new_prefix / relative_path


def listdir_matching(directory: Path, pattern: str) -> List[Path]:
    files = os.listdir(directory)
    matches = fnmatch.filter(files, pattern)
    return [directory / m for m in matches]


def unar(file: Path) -> None:
    run_command(f"unar '{file}'", cwd=file.parent, stdout=CONSOLE.stdout_console.file)
