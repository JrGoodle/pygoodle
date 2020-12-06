"""File system utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

# import errno
import fnmatch
import os
import shutil
from pathlib import Path
from typing import List, Optional

from .command import run_command


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


def make_dir(dir_path: Path, exist_ok: bool = False) -> None:
    os.makedirs(dir_path, exist_ok=exist_ok)


def move(input_path: Path, output_path: Path) -> None:
    shutil.move(str(input_path), str(output_path))


def remove_dir(dir_path: Path, ignore_errors: bool = False) -> None:
    shutil.rmtree(str(dir_path), ignore_errors=ignore_errors)


def remove_file(file: Path) -> None:
    os.remove(str(file))


def remove(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        remove_dir(path)
    elif path.is_file():
        remove_file(path)


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
    run_command(f"unar '{file}'", cwd=file.parent)


def create_backup_file(file: Path) -> None:
    """Copy file to {file}.backup

    :param Path file: File path to copy
    """

    shutil.copyfile(str(file), f"{str(file)}.backup")


def restore_from_backup_file(file: Path) -> None:
    """Copy {file}.backup to file

    :param Path file: File path to copy
    """

    shutil.copyfile(f"{file}.backup", file)


# def make_dir(directory: Path, check: bool = True) -> None:
#     """Make directory if it doesn't exist
#
#     :param str directory: Directory path to create
#     :param bool check: Whether to raise exceptions
#     """
#
#     if directory.exists():
#         return
#
#     try:
#         os.makedirs(str(directory))
#     except OSError as err:
#         if err.errno == errno.EEXIST:
#             LOG.error(f"Directory already exists at {Format.path(directory)}")
#         else:
#             LOG.error(f"Failed to create directory {Format.path(directory)}")
#         if check:
#             raise


# def remove_directory(dir_path: Path, check: bool = True) -> None:
#     """Remove directory at path
#
#     :param str dir_path: Path to directory to remove
#     :param bool check: Whether to raise errors
#     """
#
#     try:
#         shutil.rmtree(dir_path)
#     except shutil.Error:
#         LOG.error(f"Failed to remove directory {Format.path(dir_path)}")
#         if check:
#             raise


def is_directory_empty(path: Path) -> bool:
    if path.exists() and path.is_dir():
        if not os.listdir(path):
            return True
        else:
            return False
    else:
        raise Exception(f"Directory at {path} doesn't exist")


def create_file(path: Path, contents: str) -> None:
    with path.open('w') as f:
        f.write(contents)
    assert path.is_file()
    assert not path.is_symlink()
    assert path.read_text().strip() == contents.strip()


def symlink_to(path: Path, target: Path) -> None:
    parent = path.parent
    fd = os.open(parent, os.O_DIRECTORY)
    os.symlink(target, path, dir_fd=fd)
    os.close(fd)
    assert path.exists()
    assert path.is_symlink()
    assert is_relative_symlink_from_to(path, str(target))


def copy_file(path: Path, destination: Path) -> None:
    shutil.copyfile(path, destination)
    assert destination.is_file()
    assert not destination.is_symlink()


def is_relative_symlink_from_to(symlink: Path, destination: str) -> bool:
    if not symlink.is_symlink():
        return False
    path = symlink.parent
    resolved_symlink = symlink.resolve()
    if not resolved_symlink.samefile(path / destination):
        return False
    link = os.readlink(symlink)
    is_relative = not Path(link).is_absolute()
    if not is_relative:
        return False
    return True


def copy_directory(from_dir: Path, to: Path):
    # TODO: Replace rmdir() with copytree(dirs_exist_ok=True) when support for Python 3.7 is dropped
    to.rmdir()
    shutil.copytree(from_dir, to, symlinks=True)
