"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.format import GitFormat
from pygoodle.git.decorators import error_msg
from pygoodle.git.model import LocalBranch, RemoteBranch


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

    def delete_upstream(self) -> None:
        self.upstream_branch.delete()

    @property
    def is_tracking_branch(self) -> bool:
        return True

    @property
    def exists(self) -> bool:
        branches = factory.get_tracking_branches(self.path)
        return any([branch == self for branch in branches])

    @property
    def upstream_sha(self) -> Optional[str]:
        """Commit sha"""
        return offline.get_branch_commit_sha(self.path, self.upstream_branch.name, self.upstream_branch.remote.name)

    @error_msg('Failed to set tracking branch')
    def set_upstream(self) -> None:
        CONSOLE.stdout(f' - Set tracking branch {GitFormat.ref(self.short_ref)} -> '
                       f'{GitFormat.remote(self.upstream_branch.remote.name)} '
                       f'{GitFormat.ref(self.upstream_branch.short_ref)}')
        offline.set_upstream_branch(self.path,
                                    branch=self.name,
                                    upstream_branch=self.upstream_branch.name,
                                    remote=self.upstream_branch.remote.name)

    @error_msg('Failed to create tracking branch')
    def create_upstream(self) -> None:
        CONSOLE.stdout(f' - Create tracking branch {GitFormat.ref(self.short_ref)}')
        online.create_upstream_branch(self.path,
                                      branch=self.name,
                                      upstream_branch=self.upstream_branch.name,
                                      remote=self.upstream_branch.remote.name)

    def _set_tracking_branch_commit(self, branch: str, remote: str, depth: int) -> None:
        """Set tracking relationship between local and remote branch if on same commit

        :param str branch: Branch name
        :param str remote: Remote name
        :param int depth: Git clone depth. 0 indicates full clone, otherwise must be a positive integer
        :raise ClowderGitError:
        """

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
