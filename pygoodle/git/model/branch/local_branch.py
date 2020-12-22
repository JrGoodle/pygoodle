"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Optional

from pygoodle.console import CONSOLE
from pygoodle.format import Format
from pygoodle.git.constants import ORIGIN
from pygoodle.git.decorators import error_msg, not_detached
from pygoodle.git.model.commit import Commit
from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .branch import Branch


class LocalBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    """

    @property
    def is_tracking_branch(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        branches = GitFactory.get_tracking_branches(self.path)
        return any([branch.name == self.name for branch in branches])

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        return GitOffline.get_branch_commit_sha(self.path, self.name)

    @error_msg('Failed to create local branch')
    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Local branch {Format.Git.ref(self.short_ref)} already exists')
            return
        CONSOLE.stdout(f' - Create local branch {Format.Git.ref(self.short_ref)}')
        GitOffline.create_local_branch(self.path, branch=self.name)

    @error_msg('Failed to delete local branch')
    def delete(self, force: bool = False) -> None:
        if not self.exists:
            CONSOLE.stdout(f" - Local branch {Format.Git.ref(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete local branch {Format.Git.ref(self.short_ref)}')
        GitOffline.delete_local_branch(self.path, self.name, force=force)

    @property
    def exists(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_local_branch(self.path, self.name)

    @property
    def commit(self) -> Commit:
        sha = GitOffline.get_branch_commit_sha(self.path, branch=self.name)
        return Commit(self.path, sha)

    @not_detached
    @error_msg('Failed to push local changes')
    def push(self, branch: str = 'master', remote: str = ORIGIN, force: bool = False) -> None:
        CONSOLE.stdout(' - Push local changes')
        GitOnline.push(self.path,
                       local_branch=self.name,
                       remote_branch=branch,
                       remote=remote,
                       force=force)
