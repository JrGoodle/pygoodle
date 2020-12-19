"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import error_msg, not_detached
from pygoodle.git.model import Branch, Commit, RemoteBranch


class LocalBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    """

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        return offline.get_branch_commit_sha(self.path, self.name)

    def create(self) -> None:
        offline.create_local_branch(self.path, branch=self.name)

    def delete(self) -> None:
        offline.delete_local_branch(self.path, branch=self.name)

    @property
    def exists(self) -> bool:
        branches = factory.get_local_branches(self.path)
        return any([branch == self for branch in branches])

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
