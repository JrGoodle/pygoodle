"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.model.factory as factory
import pygoodle.git.online as online
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import error_msg
from pygoodle.git.format import GitFormat
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
            CONSOLE.stdout(f' - Remote tag {GitFormat.ref(self.name)} already exists')
            return
        raise NotImplementedError

    @error_msg('Failed to delete remote tag')
    def delete(self) -> None:
        # TODO: Check if tag exists
        CONSOLE.stdout(f' - Delete remote tag {GitFormat.ref(self.short_ref)}')
        online.delete_remote_tag(self.path, name=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        tags = factory.get_remote_tags(self.remote)
        return any([tag == self for tag in tags])
