"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

from pygoodle.console import CONSOLE
from pygoodle.format import Format

from ...decorators import error_msg
from ...online import GitOnline
from ..remote import Remote
from .tag import Tag


class RemoteTag(Tag):
    """Class encapsulating git tag

    :ivar Path path: Path to git repo
    :ivar str name: Tag name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str, remote: str):
        """GitRepo __init__

        :param str name: Tag name
        :param Remote remote: Remote
        """

        super().__init__(path, name)
        self.remote: Remote = Remote(self.path, remote)

    def __eq__(self, other) -> bool:
        if isinstance(other, RemoteTag):
            return super().__eq__(other) and self.remote.name == other.remote.name
        return False

    @property
    def sha(self) -> str:
        """Commit sha"""
        return GitOnline.get_remote_tag_sha(self.path, self.name, self.remote.name)

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
        GitOnline.delete_remote_tag(self.path, name=self.name, remote=self.remote.name)

    @property
    def exists(self) -> bool:
        from pygoodle.git.model.factory import GitFactory
        return GitFactory.has_remote_tag(self.path, self.name, self.remote.name)
