"""Base Git utility class

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

from pygoodle.git.constants import ORIGIN
from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .repo import Repo


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
        self.submodule_git_dir: Optional[Path] = GitOffline.get_submodule_git_dir(self.path)
        self.url: str = url
        self.commit: str = commit
        self.branch: Optional[str] = branch
        self.active: Optional[bool] = active

    @property
    def exists(self) -> bool:
        return GitOffline.is_submodule_cloned(self.path, self.submodule_path)

    @property
    def is_initialized(self) -> bool:
        # TODO: Also check for .git dir in addition to .git file pointing to .git dir in superproject git dir
        return GitOffline.is_submodule_initialized(self.path, self.submodule_path)

    def absorbgitdirs(self) -> None:
        GitOffline.submodule_absorbgitdirs(self.repo_path, paths=[self.submodule_path])

    def add(self, repo: str, branch: Optional[str] = None, force: bool = False,
            name: Optional[str] = None, reference: Optional[str] = None, depth: Optional[int] = None,
            submodule_path: Optional[Path] = None) -> None:
        GitOffline.submodule_add(self.repo_path, repo, branch=branch, force=force, name=name,
                                 reference=reference, depth=depth, submodule_path=submodule_path)

    def deinit(self, force: bool = False) -> None:
        GitOffline.submodule_deinit(self.repo_path, force=force, paths=[self.submodule_path])

    def init(self) -> None:
        GitOffline.submodule_init(self.repo_path, paths=[self.submodule_path])

    def set_branch(self, branch: str) -> None:
        GitOffline.submodule_set_branch(self.repo_path, self.submodule_path, branch)

    def set_url(self, url: str) -> None:
        GitOffline.submodule_set_url(self.repo_path, self.submodule_path, url)

    def unset_branch(self) -> None:
        GitOffline.submodule_unset_branch(self.repo_path, self.submodule_path)

    def sync(self, recursive: bool = False) -> None:
        GitOffline.submodule_sync(self.repo_path, recursive=recursive, paths=[self.submodule_path])

    def update(self, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
               jobs: Optional[int] = None, recursive: bool = False, checkout: bool = False,
               rebase: bool = False, merge: bool = False) -> None:
        GitOnline.submodule_update(self.repo_path, init=init, depth=depth, single_branch=single_branch, jobs=jobs,
                                   recursive=recursive, checkout=checkout, merge=merge, rebase=rebase,
                                   paths=[self.submodule_path])
