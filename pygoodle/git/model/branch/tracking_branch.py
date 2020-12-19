"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from . import LocalBranch, RemoteBranch


class TrackingBranch(LocalBranch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Local branch name
    :ivar RemoteBranch upstream_branch: Upstream branch name
    :ivar Optional[RemoteBranch] push_branch: Push branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str, upstream_branch: RemoteBranch,
                 push_branch: Optional[RemoteBranch] = None):
        super().__init__(path, name)
        self.upstream_branch: RemoteBranch = upstream_branch
        self.push_branch: Optional[RemoteBranch] = push_branch

    def __eq__(self, other) -> bool:
        if isinstance(other, TrackingBranch):
            return super().__eq__(other) and self.upstream_branch == other.upstream_branch
        return False

    @property
    def exists(self) -> bool:
        branches = factory.get_tracking_branches(self.path)
        return any([branch == self for branch in branches])

    @property
    def upstream_sha(self) -> Optional[str]:
        """Commit sha"""
        return offline.get_branch_commit_sha(self.path, self.upstream_branch.name, self.upstream_branch.remote.name)

    def set_upstream(self) -> None:
        offline.set_upstream_branch(self.path,
                                    branch=self.name,
                                    upstream_branch=self.upstream_branch.name,
                                    remote=self.upstream_branch.remote.name)

    def create_upstream(self) -> None:
        online.create_upstream_branch(self.path,
                                      branch=self.name,
                                      upstream_branch=self.upstream_branch.name,
                                      remote=self.upstream_branch.remote.name)
