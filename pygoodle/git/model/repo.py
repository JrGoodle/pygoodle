"""Base Git utility class

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.git.constants import ORIGIN
from pygoodle.git import Commit, LocalBranch, Ref, Remote, Submodule, TrackingBranch


class Repo:
    """Class encapsulating base git utilities

    :ivar Path path: Absolute path to repo
    :ivar str default_remote: Default remote name
    """

    def __init__(self, path: Path, default_remote: Optional[Remote] = None):
        """LocalRepo __init__

        :param Path path: Absolute path to repo
        :param str default_remote: Default remote name
        """

        self.path: Path = path
        self.git_dir: Path = self.path / '.git'
        self.default_remote: Optional[Remote] = default_remote

    @staticmethod
    def clone(path: Path, url: str, depth: Optional[int] = None, ref: Optional[Ref] = None,
              jobs: Optional[int] = None) -> 'Repo':
        online.clone(path, url=url, depth=depth, ref=ref, jobs=jobs)
        remote = Remote(path, ORIGIN, fetch_url=url)
        return Repo(path, default_remote=remote)

    @property
    def has_untracked_files(self) -> bool:
        return offline.has_untracked_files(self.path)

    @property
    def is_dirty(self) -> bool:
        return offline.is_dirty(self.path)

    @property
    def is_detached(self) -> bool:
        return offline.is_detached(self.path)

    @property
    def is_shallow(self) -> bool:
        return offline.is_shallow_repo(self.path)

    @property
    def is_rebase_in_progress(self) -> bool:
        return offline.is_rebase_in_progress(self.path)

    @property
    def remotes(self) -> List[Remote]:
        return offline.get_remotes(self.path)

    @property
    def submodules(self) -> Tuple[Submodule, ...]:
        submodules = offline.get_submodules(self.path)
        return tuple(sorted(submodules, key=lambda s: s.path.name))

    @property
    def tracking_branches(self) -> Tuple[TrackingBranch, ...]:
        branches = offline.get_tracking_branches(self.path)
        return tuple(sorted(branches, key=lambda b: b.name))

    @property
    def branches(self) -> Tuple[LocalBranch, ...]:
        branches = offline.get_local_branches(self.path)
        return tuple(sorted(branches, key=lambda b: b.name))

    @property
    def exists(self) -> bool:
        return offline.is_repo_cloned(self.path)

    def remote(self, name: str) -> Optional[Remote]:
        return offline.get_remote(self.path, name=name)

    @property
    def current_timestamp(self) -> str:
        return offline.current_timestamp(self.path)

    @property
    def current_branch(self) -> str:
        return offline.current_branch(self.path)

    def current_commit(self, short: bool = False) -> Commit:
        sha = offline.current_head_commit_sha(self.path, short=short)
        return Commit(self.path, sha)

    def abort_rebase(self) -> None:
        offline.abort_rebase(self.path)

    def add(self, files: List[str]) -> None:
        offline.add(self.path, files=files)

    def commit(self, message: str) -> None:
        offline.commit(self.path, message=message)

    def clean(self, untracked_directories: bool = False, force: bool = False,
              ignored: bool = False, untracked_files: bool = False) -> None:
        offline.clean(self.path, untracked_directories=untracked_directories,
                      force=force, ignored=ignored, untracked_files=untracked_files)

    def pull_lfs(self) -> None:
        online.pull_lfs(self.path)

    def reset(self, ref: Union[Ref, str] = ORIGIN, hard: bool = False) -> None:
        if isinstance(ref, Ref):
            ref = ref.short_ref
        offline.reset(self.path, ref=ref, hard=hard)

    def stash(self) -> None:
        offline.stash(self.path)

    def status(self, verbose: bool = False) -> None:
        offline.status(self.path, verbose=verbose)

    def install_lfs_hooks(self) -> None:
        offline.install_lfs_hooks(self.path)

    def reset_timestamp(self, timestamp: str, ref: Ref, author: Optional[str] = None) -> None:
        offline.reset_timestamp(self.path, timestamp=timestamp, ref=ref, author=author)

    def update_submodules(self, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
                          jobs: Optional[int] = None, recursive: bool = False) -> None:
        online.update_submodules(self.path, init=init, depth=depth, single_branch=single_branch,
                                 jobs=jobs, recursive=recursive)
