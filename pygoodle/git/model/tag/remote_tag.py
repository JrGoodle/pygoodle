"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

import pygoodle.git.online as online
from .. import Remote
from . import Tag


class RemoteTag(Tag):
    """Class encapsulating git tag

    :ivar Path path: Path to git repo
    :ivar str name: Tag name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str, remote: Remote):
        """GitRepo __init__

        :param Path path: Path to git repo
        :param str name: Tag name
        :param Remote remote: Remote
        """

        super().__init__(path, name)
        self.remote: Remote = remote

    def create(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        online.delete_remote_tag(self.path, name=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        return online.has_remote_tag(self.path, tag=self.name, remote=self.remote.name)
