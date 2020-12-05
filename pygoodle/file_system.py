"""File system utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

# import errno
import os
import shutil
from pathlib import Path

# from .formatting import FORMAT


def remove_file(file: Path) -> None:
    """Remove file

    :param Path file: File path to remove
    """

    os.remove(str(file))


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
#             LOG.error(f"Directory already exists at {FORMAT.path(directory)}")
#         else:
#             LOG.error(f"Failed to create directory {FORMAT.path(directory)}")
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
#         LOG.error(f"Failed to remove directory {FORMAT.path(dir_path)}")
#         if check:
#             raise
