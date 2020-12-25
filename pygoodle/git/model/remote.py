"""git remote

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional

from pygoodle.console import CONSOLE
from pygoodle.format import Format
from pygoodle.git.decorators import error_msg
from pygoodle.git.log import LOG
from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .branch.remote_branch import RemoteBranch
from .ref import Ref


class Remote:
    """Class encapsulating git ref

    :ivar Path path: Path to git repo
    :ivar str name: Branch
    :ivar str fetch_url: Fetch url
    :ivar str push_url: Push url
    """

    def __init__(self, path: Path, name: str):
        """GitRemote __init__

        :param Path path: Path to git repo
        :param str name: Branch
        """

        self.name: str = name
        self.path: Path = path

    @property
    def fetch_url(self) -> str:
        return GitOffline.get_remote_fetch_url(self.path, self.name)

    @property
    def push_url(self) -> str:
        return GitOffline.get_remote_push_url(self.path, self.name)

    @property
    def branches(self) -> List[RemoteBranch]:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.get_remote_branches(self.path, self.name)

    @error_msg('Failed to create remote')
    def create(self, url: str, fetch: bool = False, tags: bool = False) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Remote {Format.Git.remote(self.name)} already exists')
            return
        CONSOLE.stdout(f' - Create remote {Format.Git.remote(self.name)}')
        GitOffline.create_remote(self.path, name=self.name, url=url, fetch=fetch, tags=tags)

    @property
    def exists(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_remote_with_name(self.path, self.name)

    def default_branch(self, git_dir: Path, url: str) -> Optional[RemoteBranch]:
        if GitOffline.is_repo_cloned(self.path):
            default_branch = GitOffline.get_default_branch(self.path, self.name)
            if default_branch is not None:
                return RemoteBranch(self.path, default_branch, self.name)
        default_branch = GitOnline.get_default_branch(url)
        if default_branch is None:
            return None
        if git_dir.is_dir():
            GitOffline.save_default_branch(git_dir, self.name, default_branch)
        return RemoteBranch(self.path, default_branch, self.name)

    @error_msg('Failed to rename remote')
    def rename(self, name: str) -> None:
        CONSOLE.stdout(f' - Rename remote {Format.Git.remote(self.name)} to {Format.Git.remote(name)}')
        GitOffline.rename_remote(self.path, old_name=self.name, new_name=name)
        self.name = name

    def fetch(self, prune: bool = False, tags: bool = False, depth: Optional[int] = None,
              ref: Optional[Ref] = None, check: bool = True) -> None:
        output = self.name
        if ref is not None:
            ref = ref.short_ref
            output = f'{output} {ref.short_ref}'
        CONSOLE.stdout(f'Fetch from {output}')
        try:
            GitOnline.fetch(self.path, prune=prune, tags=tags, depth=depth, remote=self.name, ref=ref)
        except Exception:  # noqa
            message = f'Failed to fetch from {output}'
            if check:
                LOG.error(message)
                raise
            CONSOLE.stdout(f' - {message}')

    def print_branches(self) -> None:
        raise NotImplementedError

    def _compare_remote_url(self, remote: str, url: str) -> None:
        """Compare actual remote url to given url

        If URL's are different print error message and exit

        :param str remote: Remote name
        :param str url: URL to compare with remote's URL
        :raise ClowderGitError:
        """

        # if url != self._remote_get_url(remote):
        #     actual_url = self._remote_get_url(remote)
        #     message = f"Remote {fmt.remote(remote)} already exists with a different url\n" \
        #               f"{fmt.url_string(actual_url)} should be {fmt.url_string(url)}"
        #     raise ClowderGitError(message)
