"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

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
