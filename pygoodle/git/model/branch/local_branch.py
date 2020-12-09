"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Optional

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from .. import Commit
from . import Branch, RemoteBranch


class LocalBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    """

    def create(self) -> None:
        offline.create_local_branch(self.path, branch=self.name)

    def delete(self) -> None:
        offline.delete_local_branch(self.path, branch=self.name)

    @property
    def exists(self) -> bool:
        return offline.has_local_branch(self.path, branch=self.name)

    @property
    def commit(self) -> Commit:
        sha = offline.get_branch_commit_sha(self.path, branch=self.name)
        return Commit(self.path, sha)

    def push(self, branch: Optional[RemoteBranch] = None, force: bool = False) -> None:
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
