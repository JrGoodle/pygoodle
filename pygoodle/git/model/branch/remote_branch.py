"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from .. import Commit, Remote
from . import Branch


class RemoteBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str, remote: Remote):
        """Branch __init__

        :param Path path: Path to git repo
        :param str name: Branch name
        :param Remote remote: Remote
        """

        super().__init__(path, name)
        self.remote: Remote = remote

    def delete(self) -> None:
        online.delete_remote_branch(self.path, branch=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        return online.has_remote_branch(self.path, branch=self.name, remote=self.remote.name)

    def create(self) -> None:
        raise NotImplementedError

    @property
    def commit(self) -> Commit:
        sha = offline.get_branch_commit_sha(self.path, branch=self.name, remote=self.name)
        return Commit(self.path, sha)

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.format_git_branch(self.name)
