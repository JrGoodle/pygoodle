"""Base Git utility class

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.git.constants import ORIGIN
from . import Repo


class Submodule(Repo):
    """Class encapsulating base git utilities

    :ivar Path path: Absolute path to repo
    :ivar Path submodule_path: Relative path to submodule
    """

    def __init__(self, repo_path: Path, submodule_path: Path, url: str, commit: str,
                 branch: Optional[str] = None, active: Optional[bool] = None):
        """LocalRepo __init__

        :param Path repo_path: Absolute path to repo
        :param Path submodule_path: Relative path to submodule
        :param str url: Remote url
        :param str commit: Current commit sha stored in git tree
        :param Optional[str] branch: Branch to track
        :param Optional[bool] active: Whether submodule is active
        """

        super().__init__(repo_path, default_remote=ORIGIN)
        self.repo_path: Path = repo_path
        self.submodule_path: Path = submodule_path
        self.path: Path = self.path / self.submodule_path
        self.submodule_git_dir: Optional[Path] = offline.get_submodule_git_dir(self.path)
        self.url: str = url
        self.commit: str = commit
        self.branch: Optional[str] = branch
        self.active: Optional[bool] = active

    @property
    def exists(self) -> bool:
        return offline.is_submodule_cloned(self.path, self.submodule_path)

    @property
    def is_initialized(self) -> bool:
        return offline.is_submodule_initialized(self.path, self.submodule_path)

    def update(self, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
               jobs: Optional[int] = None, recursive: bool = False) -> None:
        online.update_submodules(self.repo_path, init=init, depth=depth, single_branch=single_branch,
                                 jobs=jobs, recursive=recursive, paths=[self.submodule_path])
