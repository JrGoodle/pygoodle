"""git remote

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from . import Ref, RemoteBranch


class Remote:
    """Class encapsulating git ref

    :ivar Path path: Path to git repo
    :ivar str name: Branch
    :ivar str fetch_url: Fetch url
    :ivar str push_url: Push url
    """

    def __init__(self, path: Path, name: str, fetch_url: str, push_url: Optional[str] = None):
        """GitRemote __init__

        :param Path path: Path to git repo
        :param str name: Branch
        :param str fetch_url: Fetch url
        :param Optional[str] push_url: Push url
        """

        self.name: str = name
        self.path: Path = path
        self.fetch_url: str = fetch_url
        self.push_url: str = fetch_url if push_url is None else push_url

    def branches(self) -> List[RemoteBranch]:
        return offline.get_remote_branches(self.path, remote=self)

    def create(self, fetch: bool = False, tags: bool = False) -> None:
        offline.create_remote(self.path, name=self.name, url=self.fetch_url, fetch=fetch, tags=tags)

    def pull(self, branch: Optional[str] = None) -> None:
        online.pull(self.path, remote=self.name, branch=branch)

    def default_branch(self, save: bool = True) -> RemoteBranch:
        if offline.is_repo_cloned(self.path):
            default_branch = offline.get_default_branch(self.path, self.name)
            if default_branch is not None:
                return RemoteBranch(self.path, name=default_branch, remote=self)

        default_branch = online.get_default_branch(self.fetch_url)
        if save:
            offline.save_default_branch(self.path, self.name, self.fetch_url)
        return RemoteBranch(self.path, name=default_branch, remote=self)

    def rename(self, name: str) -> None:
        offline.rename_remote(self.path, old_name=self.name, new_name=name)
        self.name = name

    def fetch(self, prune: bool = False, tags: bool = False, depth: Optional[int] = None,
              ref: Optional[Ref] = None) -> None:
        online.fetch(self.path, prune=prune, tags=tags, depth=depth, remote=self.name, ref=ref)
