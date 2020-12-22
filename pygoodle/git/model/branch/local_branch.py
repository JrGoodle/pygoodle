"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.format import Format
from pygoodle.git.decorators import error_msg, not_detached
from pygoodle.git.model import Branch, Commit, RemoteBranch


class LocalBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    """

    @property
    def is_tracking_branch(self) -> bool:
        branches = factory.get_tracking_branches(self.path)
        return any([branch.name == self.name for branch in branches])

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        return offline.get_branch_commit_sha(self.path, self.name)

    @error_msg('Failed to create local branch')
    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Local branch {Format.Git.ref(self.short_ref)} already exists')
            return
        CONSOLE.stdout(f' - Create local branch {Format.Git.ref(self.short_ref)}')
        offline.create_local_branch(self.path, branch=self.name)

    @error_msg('Failed to delete local branch')
    def delete(self, force: bool = False) -> None:
        if not self.exists:
            CONSOLE.stdout(f" - Local branch {Format.Git.ref(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete local branch {Format.Git.ref(self.short_ref)}')
        offline.delete_local_branch(self.path, self.name, force=force)

    @property
    def exists(self) -> bool:
        return factory.has_local_branch(self.path, self.name)

    @property
    def commit(self) -> Commit:
        sha = offline.get_branch_commit_sha(self.path, branch=self.name)
        return Commit(self.path, sha)

    @not_detached
    @error_msg('Failed to push local changes')
    def push(self, branch: Optional[RemoteBranch] = None, force: bool = False) -> None:
        CONSOLE.stdout(' - Push local changes')
        remote_branch = None
        remote = None
        if branch is not None:
            remote_branch = branch.name
            remote = branch.remote.name
        online.push(self.path,
                    local_branch=self.name,
                    remote_branch=remote_branch,
                    remote=remote,
                    force=force)
