"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.model.factory as factory
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import error_msg
from pygoodle.format import Format
from pygoodle.git.model import Remote, Tag


class RemoteTag(Tag):
    """Class encapsulating git tag

    :ivar Path path: Path to git repo
    :ivar str name: Tag name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, name: str, remote: Remote):
        """GitRepo __init__

        :param str name: Tag name
        :param Remote remote: Remote
        """

        super().__init__(remote.path, name)
        self.remote: Remote = remote

    def __eq__(self, other) -> bool:
        if isinstance(other, RemoteTag):
            return super().__eq__(other) and self.remote.name == other.remote.name
        return False

    @property
    def sha(self) -> str:
        """Commit sha"""
        return online.get_remote_tag_sha(self.path, self.name, self.remote.name)

    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Remote tag {Format.Git.ref(self.name)} already exists')
            return
        raise NotImplementedError

    @error_msg('Failed to delete remote tag')
    def delete(self) -> None:
        if not self.exists:
            CONSOLE.stdout(f" - Remote tag {Format.Git.ref(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete remote tag {Format.Git.ref(self.short_ref)}')
        online.delete_remote_tag(self.path, name=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        return factory.has_remote_tag(self.name, self.remote)
