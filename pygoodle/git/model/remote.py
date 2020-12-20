"""git remote

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.format import GitFormat
from pygoodle.git.decorators import error_msg, not_detached
from pygoodle.git.model import Ref, RemoteBranch
from pygoodle.git.log import LOG


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
        return offline.get_remote_fetch_url(self.path, self.name)

    @property
    def push_url(self) -> str:
        return offline.get_remote_push_url(self.path, self.name)

    @property
    def branches(self) -> List[RemoteBranch]:
        return factory.get_remote_branches(self)

    @error_msg('Failed to create remote')
    def create(self, url: str, fetch: bool = False, tags: bool = False) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Remote {GitFormat.remote(self.name)} already exists')
            return
        CONSOLE.stdout(f' - Create remote {GitFormat.remote(self.name)}')
        offline.create_remote(self.path, name=self.name, url=url, fetch=fetch, tags=tags)

    @property
    def exists(self) -> bool:
        raise NotImplementedError

    @not_detached
    @error_msg('Failed to pull')
    def pull(self, branch: Optional[str] = None, rebase: bool = False) -> None:
        message = f' - Pull'
        if rebase:
            message += ' with rebase'
        message += f' from {GitFormat.remote(self.name)}'
        if branch is not None:
            message += f' {GitFormat.ref(branch)}'
        CONSOLE.stdout(message)
        online.pull(self.path, remote=self.name, branch=branch, rebase=rebase)

    @property
    def default_branch(self) -> RemoteBranch:
        if offline.is_repo_cloned(self.path):
            default_branch = offline.get_default_branch(self.path, self.name)
            if default_branch is not None:
                return RemoteBranch(name=default_branch, remote=self)

        default_branch = online.get_default_branch(self.fetch_url)
        # FIXME: Need to use git_dir here instead of path
        offline.save_default_branch(self.path, self.name, self.fetch_url)
        return RemoteBranch(name=default_branch, remote=self)

    @error_msg('Failed to rename remote')
    def rename(self, name: str) -> None:
        CONSOLE.stdout(f' - Rename remote {GitFormat.remote(self.name)} to {GitFormat.remote(name)}')
        offline.rename_remote(self.path, old_name=self.name, new_name=name)
        self.name = name

    def fetch(self, prune: bool = False, tags: bool = False, depth: Optional[int] = None,
              ref: Optional[Ref] = None, check: bool = True) -> None:
        output = self.name
        if ref is not None:
            output = f'{output} {ref.short_ref}'
        CONSOLE.stdout(f'Fetch from {output}')
        try:
            online.fetch(self.path, prune=prune, tags=tags, depth=depth, remote=self.name, ref=ref.short_ref)
        except Exception:  # noqa
            message = f'Failed to fetch from {output}'
            if check:
                LOG.error(message)
                raise
            CONSOLE.stdout(f' - {message}')

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
