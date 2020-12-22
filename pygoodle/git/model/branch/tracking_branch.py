"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import not_detached
from pygoodle.format import Format
from pygoodle.git.decorators import error_msg
from pygoodle.git.model import Branch, LocalBranch, RemoteBranch


class TrackingBranch(Branch):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Local branch name
    :ivar RemoteBranch upstream_branch: Upstream branch name
    :ivar Optional[RemoteBranch] push_branch: Push branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, local_branch: str, upstream_branch: str, upstream_remote: str,
                 push_branch: Optional[str] = None, push_remote: Optional[str] = None):
        super().__init__(path, local_branch)
        self.local_branch: LocalBranch = LocalBranch(self.path, self.name)
        self.upstream_branch: RemoteBranch = RemoteBranch(self.path, upstream_branch, upstream_remote)
        push_branch = upstream_branch if push_branch is None else push_branch
        push_remote = upstream_remote if push_remote is None else push_remote
        self.push_branch: RemoteBranch = RemoteBranch(self.path, push_branch, push_remote)

    def __eq__(self, other) -> bool:
        if isinstance(other, TrackingBranch):
            return super().__eq__(other) and self.upstream_branch == other.upstream_branch
        return False

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        raise self.local_branch.sha

    def delete(self) -> None:
        self.local_branch.delete()
        self.upstream_branch.delete()

    @property
    def is_branch(self) -> bool:
        return True

    @property
    def is_tracking_branch(self) -> bool:
        return True

    @property
    def exists(self) -> bool:
        return factory.has_tracking_branch(self.path, self.name)

    @error_msg('Failed to set tracking branch')
    def set_upstream(self, name: Optional[str] = None) -> None:
        name = self.name if name is None else name
        CONSOLE.stdout(f' - Set tracking branch {Format.Git.ref(self.short_ref)} -> '
                       f'{Format.Git.remote(self.upstream_branch.remote.name)} '
                       f'{Format.Git.ref(self.upstream_branch.short_ref)}')
        offline.set_upstream_branch(self.path,
                                    branch=name,
                                    upstream_branch=self.upstream_branch.name,
                                    remote=self.upstream_branch.remote.name)

    @error_msg('Failed to create tracking branch')
    def create_upstream(self) -> None:
        if self.upstream_branch.exists:
            CONSOLE.stdout(' - Tracking branch already exists')
            return
        CONSOLE.stdout(f' - Create tracking branch {Format.Git.ref(self.short_ref)}')
        online.create_upstream_branch(self.path,
                                      branch=self.name,
                                      upstream_branch=self.upstream_branch.name,
                                      remote=self.upstream_branch.remote.name)

    @not_detached
    @error_msg('Failed to pull')
    def pull(self, rebase: bool = False) -> None:
        message = f' - Pull'
        if rebase:
            message += ' with rebase'
        message += f' from {Format.Git.remote(self.upstream_branch.remote.name)} ' \
                   f'{Format.Git.ref(self.upstream_branch.name)}'
        CONSOLE.stdout(message)
        online.pull(self.path, remote=self.upstream_branch.remote.name, branch=self.upstream_branch.name, rebase=rebase)

    def _set_tracking_branch_commit(self, branch: str, remote: str, depth: int) -> None:
        """Set tracking relationship between local and remote branch if on same commit

        :param str branch: Branch name
        :param str remote: Remote name
        :param int depth: Git clone depth. 0 indicates full clone, otherwise must be a positive integer
        :raise ClowderGitError:
        """

        # FIXME: Try to set this in any scenario where it makes sense
        # origin = self._remote(remote)
        # self.fetch(remote, depth=depth, ref=GitRef(branch=branch))
        #
        # if not self.has_local_branch(branch):
        #     raise ClowderGitError(f'No local branch {fmt.ref(branch)}')
        #
        # if not self.has_remote_branch(branch, remote):
        #     raise ClowderGitError(f'No remote branch {fmt.ref(branch)}')
        #
        # local_branch = self.repo.heads[branch]
        # remote_branch = origin.refs[branch]
        # if local_branch.commit != remote_branch.commit:
        #     raise ClowderGitError(f' - Existing remote branch {fmt.ref(branch)} on different commit')
        #
        # self._set_tracking_branch(remote, branch)
