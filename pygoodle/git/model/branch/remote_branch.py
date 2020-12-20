"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.format import Format
from pygoodle.git.decorators import error_msg
from pygoodle.git.model import Branch, Commit, Remote


class RemoteBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, name: str, remote: Remote, is_default: bool = False):
        """Branch __init__

        :param str name: Branch name
        :param Remote remote: Remote
        :param bool is_default: Is branch default for remote repo
        """

        super().__init__(remote.path, name)
        self.remote: Remote = remote
        self.is_default: bool = is_default

    def __eq__(self, other) -> bool:
        if isinstance(other, RemoteBranch):
            return super().__eq__(other) and self.remote.name == other.remote.name
        return False

    @property
    def is_tracking_branch(self) -> bool:
        branches = factory.get_tracking_branches(self.path)
        return any([branch.upstream_branch == self for branch in branches])

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        return offline.get_branch_commit_sha(self.path, self.name, self.remote.name)

    @error_msg('Failed to delete remote branch')
    def delete(self) -> None:
        if factory.has_remote_branch(self.path, self.name):
            CONSOLE.stdout(f" - Remote branch {Format.magenta(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete remote branch {Format.magenta(self.short_ref)}')
        online.delete_remote_branch(self.path, branch=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        branches = factory.get_remote_branches(self.remote)
        return any([branch == self for branch in branches])

    @error_msg('Failed to create remote branch')
    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Remote branch {Format.magenta(self.short_ref)} already exists')
            return
        CONSOLE.stdout(f' - Create remote branch {Format.magenta(self.short_ref)}')
        raise NotImplementedError

    @property
    def commit(self) -> Commit:
        sha = offline.get_branch_commit_sha(self.path, branch=self.name, remote=self.name)
        return Commit(self.path, sha)

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.format_git_branch(self.name)
