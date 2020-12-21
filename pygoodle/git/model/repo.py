"""Base Git utility class

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional, Union

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.format import Format
from pygoodle.git import GitConfig
from pygoodle.git.constants import ORIGIN
from pygoodle.git.model import (
    AllBranches,
    Branch,
    Commit,
    LocalBranch,
    Ref,
    Remote,
    RemoteBranch,
    Submodule,
    TrackingBranch
)
from pygoodle.git.decorators import error_msg


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
        branch = ref.short_ref if isinstance(ref, Branch) else None
        online.clone(path, url=url, depth=depth, branch=branch, jobs=jobs)
        if not isinstance(ref, Branch):
            offline.checkout(path, ref.sha)
        remote = Remote(path, ORIGIN)
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
        return factory.get_remotes(self.path)

    @property
    def submodules(self) -> List[Submodule]:
        return factory.get_submodules(self.path)

    @property
    def tracking_branches(self) -> List[TrackingBranch]:
        return factory.get_tracking_branches(self.path)

    @property
    def local_branches(self) -> List[LocalBranch]:
        return factory.get_local_branches(self.path)

    @property
    def remote_branches(self) -> List[RemoteBranch]:
        return factory.get_all_remote_branches(self.path)

    @property
    def all_branches(self) -> AllBranches:
        return factory.get_all_branches(self.path)

    def has_local_branch(self, name: str) -> bool:
        return factory.has_local_branch(self.path, name)

    @staticmethod
    def has_remote_branch(name: str, remote: Remote) -> bool:
        return factory.has_remote_branch(name, remote)

    def has_tracking_branch(self, name: str) -> bool:
        return factory.has_tracking_branch(self.path, name)

    @property
    def exists(self) -> bool:
        return offline.is_repo_cloned(self.path)

    def is_valid(self, allow_missing: bool = True) -> bool:
        """Validate repo state

        :param bool allow_missing: Whether to allow validation to succeed with missing repo
        :return: True, if repo not dirty or doesn't exist on disk
        """

        if not self.exists:
            return allow_missing

        return self.is_dirty or self.is_rebase_in_progress or self.has_untracked_files

    def remote(self, name: str) -> Optional[Remote]:
        return factory.get_remote(self.path, name)

    @property
    def current_timestamp(self) -> str:
        return offline.current_timestamp(self.path)

    @property
    def current_branch(self) -> str:
        return offline.current_branch(self.path)

    def current_commit(self, short: bool = False) -> Commit:
        sha = offline.current_head_commit_sha(self.path, short=short)
        return Commit(self.path, sha)

    @error_msg('Failed to abort rebase')
    def abort_rebase(self) -> None:
        if not self.is_rebase_in_progress:
            return
        CONSOLE.stdout(' - Abort rebase in progress')
        offline.abort_rebase(self.path)

    @error_msg('Failed to add files to git index')
    def add(self, files: List[str]) -> None:
        CONSOLE.stdout(' - Add files to git index')
        offline.add(self.path, files=files)

    @error_msg('Failed to commit current changes')
    def commit(self, message: str) -> None:
        CONSOLE.stdout(' - Commit current changes')
        offline.commit(self.path, message=message)

    def clean(self, untracked_directories: bool = False, force: bool = False,
              ignored: bool = False, untracked_files: bool = False) -> None:
        """Discard changes for repo

        :param bool untracked_directories: ``d`` Remove untracked directories in addition to untracked files
        :param bool force: ``f`` Delete directories with .git sub directory or file
        :param bool ignored: ``X`` Remove only files ignored by git
        :param bool untracked_files: ``x`` Remove all untracked files
        """
        CONSOLE.stdout(' - Clean repo')
        offline.clean(self.path, untracked_directories=untracked_directories,
                      force=force, ignored=ignored, untracked_files=untracked_files)

    @error_msg('Failed to pull git lfs files')
    def pull_lfs(self) -> None:
        CONSOLE.stdout(' - Pull git lfs files')
        online.pull_lfs(self.path)

    @error_msg('Failed to reset repo')
    def reset(self, ref: Union[Ref, str] = ORIGIN, hard: bool = False) -> None:
        if isinstance(ref, Ref):
            ref = ref.short_ref
        CONSOLE.stdout(f' - Reset repo to {Format.Git.ref(ref)}')
        offline.reset(self.path, ref=ref, hard=hard)

    @error_msg('Failed to stash current changes')
    def stash(self) -> None:
        if not self.is_dirty:
            CONSOLE.stdout(' - No changes to stash')
            return
        CONSOLE.stdout(' - Stash current changes')
        offline.stash(self.path)

    def status(self, verbose: bool = False) -> None:
        offline.status(self.path, verbose=verbose)

    @error_msg('Failed to update local git config')
    def update_git_config(self, config: GitConfig) -> None:
        """Update custom git config

        :param GitConfig config: Custom git config
        """

        CONSOLE.stdout(" - Update local git config")
        for key, value in config.items():
            offline.git_config_unset_all_local(self.path, key)
            offline.git_config_add_local(self.path, key, value)

    @error_msg('Failed to update git lfs hooks')
    def install_lfs_hooks(self) -> None:
        CONSOLE.stdout(' - Update git lfs hooks')
        offline.install_lfs_hooks(self.path)

    @error_msg('Failed to reset timestamp')
    def reset_timestamp(self, timestamp: str, ref: Ref, author: Optional[str] = None) -> None:
        CONSOLE.stdout(' - Reset timestamp')
        offline.reset_timestamp(self.path, timestamp=timestamp, ref=ref.short_ref, author=author)

    @error_msg('Failed to update submodules')
    def update_submodules(self, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
                          jobs: Optional[int] = None, recursive: bool = False) -> None:
        CONSOLE.stdout(' - Update submodules')
        online.update_submodules(self.path, init=init, depth=depth, single_branch=single_branch,
                                 jobs=jobs, recursive=recursive)

    def print_local_branches(self) -> None:
        """Print local git branches"""

        # FIXME: Implement
        # current_branch = self.current_branch
        # for branch in self.branches:
        #     if branch.name == current_branch:
        #         branch_name = Format.green(branch[2:])
        #         CONSOLE.stdout(f"* {branch_name}")
        #     else:
        #         CONSOLE.stdout(branch)

    def print_validation(self) -> None:
        """Print validation messages"""

        if not self.exists:
            return

        if not self.is_valid:
            CONSOLE.stdout(f'Dirty repo. Please stash, commit, or discard your changes')

    def groom(self, untracked_directories: bool = False, force: bool = False,
              ignored: bool = False, untracked_files: bool = False) -> None:
        self.clean(untracked_directories=untracked_directories,
                   force=force, ignored=ignored, untracked_files=untracked_files)
        self.reset()
        if self.is_rebase_in_progress:
            self.abort_rebase()

    @property
    def formatted_ref(self) -> str:
        """Formatted project repo ref"""

        local_commits_count = offline.new_commits_count(self.path)
        # TODO: Specify correct remote
        upstream_commits_count = offline.new_commits_count(self.path, upstream=True)
        no_local_commits = local_commits_count == 0 or local_commits_count == '0'
        no_upstream_commits = upstream_commits_count == 0 or upstream_commits_count == '0'
        if no_local_commits and no_upstream_commits:
            status = ''
        else:
            local_commits_output = Format.yellow(f'+{local_commits_count}')
            upstream_commits_output = Format.red(f'-{upstream_commits_count}')
            status = f'({local_commits_output}/{upstream_commits_output})'

        if self.is_detached:
            return Format.Git.ref(Format.escape(f'[HEAD @ {self.current_commit()}]'))
        return Format.Git.ref(Format.escape(f'[{self.current_branch}]')) + status

    def print_remote_branches(self) -> None:
        """Print remote git branches"""

        # FIXME: Update this to work
        # Need to get all local, remote, and tracking branches and print them
        # for remote in self.remotes:
        #     for branch in remote.branches:
        #     if ' -> ' in branch:
        #         components = branch.split(' -> ')
        #         local_branch = components[0]
        #         remote_branch = components[1]
        #         CONSOLE.stdout(f"  {Format.red(local_branch)} -> {remote_branch}")
        #     else:
        #         CONSOLE.stdout(Format.red(branch))
