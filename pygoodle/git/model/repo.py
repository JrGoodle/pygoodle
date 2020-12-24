"""Base Git utility class

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional, Union, TYPE_CHECKING

from pygoodle.console import CONSOLE
from pygoodle.git.decorators import not_detached
from pygoodle.format import Format
from pygoodle.git.constants import GitConfig, ORIGIN
from pygoodle.git.decorators import error_msg
from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .branch.branch import Branch
from .branch.local_branch import LocalBranch
from .branch.remote_branch import RemoteBranch
from .branch.tracking_branch import TrackingBranch
from .commit import Commit
from .protocol import Protocol
from .ref import Ref
from .remote import Remote

if TYPE_CHECKING:
    from .factory import AllBranches
    from .submodule import Submodule


class Repo:
    """Class encapsulating base git utilities

    :ivar Path path: Absolute path to repo
    :ivar str default_remote: Default remote name
    """

    def __init__(self, path: Path, default_remote: Optional[str] = None, url: Optional[str] = None,
                 protocol: Protocol = Protocol.SSH):
        """LocalRepo __init__

        :param Path path: Absolute path to repo
        :param str default_remote: Default remote name
        """

        self.path: Path = path
        self.git_dir: Path = self.path / '.git'
        self.default_remote: Optional[Remote] = Remote(self.path, default_remote)
        self.url: Optional[str] = url
        self.protocol: Protocol = protocol

    @staticmethod
    def clone(path: Path, url: str, depth: Optional[int] = None, ref: Optional[Ref] = None,
              jobs: Optional[int] = None) -> 'Repo':
        branch = ref.short_ref if isinstance(ref, Branch) else None
        GitOnline.clone(path, url=url, depth=depth, branch=branch, jobs=jobs)
        if not isinstance(ref, Branch):
            GitOffline.checkout(path, ref.sha)
        return Repo(path, default_remote=ORIGIN)

    @property
    def has_untracked_files(self) -> bool:
        return GitOffline.has_untracked_files(self.path)

    @property
    def is_dirty(self) -> bool:
        return GitOffline.is_dirty(self.path)

    @property
    def is_detached(self) -> bool:
        return GitOffline.is_detached(self.path)

    @property
    def is_shallow(self) -> bool:
        return GitOffline.is_shallow_repo(self.path)

    @property
    def is_rebase_in_progress(self) -> bool:
        return GitOffline.is_rebase_in_progress(self.path)

    @property
    def remotes(self) -> List[Remote]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_remotes(self.path)

    @property
    def submodules(self) -> List['Submodule']:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_submodules(self.path)

    @property
    def tracking_branches(self) -> List[TrackingBranch]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_tracking_branches(self.path)

    @property
    def local_branches(self) -> List[LocalBranch]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_local_branches(self.path)

    @property
    def remote_branches(self) -> List[RemoteBranch]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_all_remote_branches(self.path)

    @property
    def all_branches(self) -> 'AllBranches':
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_all_branches(self.path)

    def has_local_branch(self, name: str) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_local_branch(self.path, name)

    def has_remote_branch(self, name: str, remote: str) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_remote_branch(self.path, name, remote)

    def has_tracking_branch(self, name: str) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_tracking_branch(self.path, name)

    @property
    def exists(self) -> bool:
        return GitOffline.is_repo_cloned(self.path)

    def checkout(self, ref: str) -> None:
        if self.is_dirty:
            CONSOLE.stdout(' - Dirty repo. Please stash, commit, or discard your changes')
            self.status(verbose=True)
            return
        GitOffline.checkout(self.path, ref=ref)

    def is_valid(self, allow_missing: bool = True) -> bool:
        """Validate repo state

        :param bool allow_missing: Whether to allow validation to succeed with missing repo
        :return: True, if repo not dirty or doesn't exist on disk
        """

        if not self.exists:
            return allow_missing

        if self.is_dirty or self.is_rebase_in_progress or self.has_untracked_files:
            return False

        submodules = self.submodules
        if not submodules:
            return True
        return all([s.is_valid(allow_missing=allow_missing) for s in submodules])

    def remote(self, name: str) -> Optional[Remote]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_remote(self.path, name)

    @property
    def current_timestamp(self) -> str:
        return GitOffline.current_timestamp(self.path)

    @property
    def current_branch(self) -> str:
        return GitOffline.current_branch(self.path)

    def current_commit(self, short: bool = False) -> Commit:
        sha = GitOffline.current_head_commit_sha(self.path, short=short)
        return Commit(self.path, sha)

    @error_msg('Failed to abort rebase')
    def abort_rebase(self) -> None:
        if not self.is_rebase_in_progress:
            return
        CONSOLE.stdout(' - Abort rebase in progress')
        GitOffline.abort_rebase(self.path)

    @error_msg('Failed to add files to git index')
    def add_files(self, files: List[str]) -> None:
        CONSOLE.stdout(' - Add files to git index')
        GitOffline.add(self.path, files=files)

    @error_msg('Failed to commit current changes')
    def commit(self, message: str) -> None:
        CONSOLE.stdout(' - Commit current changes')
        GitOffline.commit(self.path, message=message)

    def clean(self, untracked_directories: bool = False, force: bool = False,
              ignored: bool = False, untracked_files: bool = False) -> None:
        """Discard changes for repo

        :param bool untracked_directories: ``d`` Remove untracked directories in addition to untracked files
        :param bool force: ``f`` Delete directories with .git sub directory or file
        :param bool ignored: ``X`` Remove only files ignored by git
        :param bool untracked_files: ``x`` Remove all untracked files
        """

        if not self.is_dirty:
            CONSOLE.stdout(' - No changes to discard')
            return

        CONSOLE.stdout(' - Clean repo')
        GitOffline.clean(self.path, untracked_directories=untracked_directories,
                         force=force, ignored=ignored, untracked_files=untracked_files)

    @error_msg('Failed to pull git lfs files')
    def pull_lfs(self) -> None:
        CONSOLE.stdout(' - Pull git lfs files')
        GitOnline.pull_lfs(self.path)

    @error_msg('Failed to reset repo')
    def reset(self, ref: Union[Ref, str] = ORIGIN, hard: bool = False) -> None:
        if isinstance(ref, Ref):
            ref = ref.short_ref
        CONSOLE.stdout(f' - Reset repo to {Format.Git.ref(ref)}')
        GitOffline.reset(self.path, ref=ref, hard=hard)

    @error_msg('Failed to stash current changes')
    def stash(self) -> None:
        if not self.is_dirty:
            CONSOLE.stdout(' - No changes to stash')
            return
        CONSOLE.stdout(' - Stash current changes')
        GitOffline.stash(self.path)

    def status(self, verbose: bool = False) -> None:
        GitOffline.status(self.path, verbose=verbose)

    @error_msg('Failed to update local git config')
    def update_git_config(self, config: GitConfig) -> None:
        """Update custom git config

        :param GitConfig config: Custom git config
        """

        CONSOLE.stdout(" - Update local git config")
        for key, value in config.items():
            GitOffline.git_config_unset_all_local(self.path, key)
            GitOffline.git_config_add_local(self.path, key, value)

    @error_msg('Failed to update git lfs hooks')
    def install_lfs_hooks(self) -> None:
        CONSOLE.stdout(' - Update git lfs hooks')
        GitOffline.install_lfs_hooks(self.path)

    @error_msg('Failed to reset timestamp')
    def reset_timestamp(self, timestamp: str, ref: Ref, author: Optional[str] = None) -> None:
        CONSOLE.stdout(' - Reset timestamp')
        GitOffline.reset_timestamp(self.path, timestamp=timestamp, ref=ref.short_ref, author=author)

    @error_msg('Failed to update submodules')
    def submodule_update(self, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
                         jobs: Optional[int] = None, recursive: bool = False, remote: bool = False,
                         checkout: bool = False, rebase: bool = False, merge: bool = False,
                         paths: Optional[List[Path]] = None) -> None:
        CONSOLE.stdout(' - Update submodules')
        GitOnline.submodule_update(self.path, init=init, depth=depth, single_branch=single_branch,
                                   jobs=jobs, recursive=recursive, remote=remote, checkout=checkout,
                                   merge=merge, rebase=rebase, paths=paths)

    @error_msg('Failed to deinit submodules')
    def submodule_deinit(self, force: bool = False, paths: Optional[List[Path]] = None) -> None:
        CONSOLE.stdout(' - Deinit submodules')
        GitOffline.submodule_deinit(self.path, force=force, paths=paths)

    @error_msg('Failed to init submodules')
    def submodule_init(self, paths: Optional[List[Path]] = None) -> None:
        CONSOLE.stdout(' - Init submodules')
        GitOffline.submodule_init(self.path, paths=paths)

    @error_msg('Failed to sync submodules')
    def submodule_sync(self, recursive: bool = False, paths: Optional[List[Path]] = None) -> None:
        CONSOLE.stdout(' - Sync submodules')
        GitOffline.submodule_sync(self.path, recursive=recursive, paths=paths)

    def print_local_branches(self) -> None:
        """Print local git branches"""

        for branch in self.local_branches:
            if branch.name == self.current_branch:
                branch_name = Format.green(branch[2:])
                CONSOLE.stdout(f'* {branch_name}')
            else:
                CONSOLE.stdout(branch)

    def print_validation(self, allow_missing: bool = False) -> None:
        """Print validation message"""

        if not self.exists or self.is_valid(allow_missing=allow_missing):
            return
        CONSOLE.stdout(self.status())
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

        if self.is_detached:
            return Format.Git.ref(Format.escape(f'[HEAD @ {self.current_commit()}]'))

        current_branch_output = Format.Git.ref(Format.escape(f'[{self.current_branch}]'))

        local_commits_count = GitOffline.new_commits_count(self.path)
        no_local_commits = local_commits_count == 0
        # TODO: Specify correct remote
        upstream_commits_count = GitOffline.new_commits_count(self.path, upstream=True)
        no_upstream_commits = upstream_commits_count == 0

        if no_local_commits and no_upstream_commits:
            return current_branch_output

        local_commits_output = Format.yellow(f'+{local_commits_count}')
        upstream_commits_output = Format.red(f'-{upstream_commits_count}')
        return f'{current_branch_output}({local_commits_output}/{upstream_commits_output})'

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

    @not_detached
    @error_msg('Failed to pull')
    def pull(self, rebase: bool = False) -> None:
        message = f' - Pull'
        if rebase:
            message += ' with rebase'
        CONSOLE.stdout(message)
        GitOnline.pull(self.path, rebase=rebase)

    @not_detached
    @error_msg('Failed to push')
    def push(self, force: bool = False) -> None:
        CONSOLE.stdout(' - Push current branch')
        GitOnline.push(self.path, force=force)
