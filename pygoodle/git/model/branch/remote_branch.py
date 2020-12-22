"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

from pygoodle.console import CONSOLE
from pygoodle.git.decorators import not_detached
from pygoodle.format import Format
from pygoodle.git.decorators import error_msg
from pygoodle.git.model.commit import Commit
from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .branch import Branch


class RemoteBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str, remote: str, is_default: bool = False):
        """Branch __init__

        :param str name: Branch name
        :param Remote remote: Remote
        :param bool is_default: Is branch default for remote repo
        """

        from pygoodle.git.model.remote import Remote
        super().__init__(path, name)
        self.remote: Remote = Remote(self.path, remote)
        self.is_default: bool = is_default

    def __eq__(self, other) -> bool:
        if isinstance(other, RemoteBranch):
            return super().__eq__(other) and self.remote.name == other.remote.name
        return False

    @property
    def is_tracking_branch(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_tracking_branch(self.path, self.name)

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        return GitOffline.get_branch_commit_sha(self.path, self.name, self.remote.name)

    @error_msg('Failed to delete remote branch')
    def delete(self) -> None:
        if not self.exists:
            CONSOLE.stdout(f" - Remote branch {Format.Git.ref(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete remote branch {Format.Git.ref(self.short_ref)}')
        GitOnline.delete_remote_branch(self.path, branch=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_remote_branch(self.path, self.name, self.remote.name)

    @error_msg('Failed to create remote branch')
    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Remote branch {Format.Git.ref(self.short_ref)} already exists')
            return
        CONSOLE.stdout(f' - Create remote branch {Format.Git.ref(self.short_ref)}')
        raise NotImplementedError

    @property
    def commit(self) -> Commit:
        sha = GitOffline.get_branch_commit_sha(self.path, branch=self.name, remote=self.name)
        return Commit(self.path, sha)

    @not_detached
    @error_msg('Failed to pull')
    def pull(self, rebase: bool = False) -> None:
        message = f' - Pull'
        if rebase:
            message += ' with rebase'
        message += f' from {Format.Git.remote(self.remote.name)} {Format.Git.ref(self.name)}'
        CONSOLE.stdout(message)
        GitOnline.pull(self.path, remote=self.remote.name, branch=self.name, rebase=rebase)
