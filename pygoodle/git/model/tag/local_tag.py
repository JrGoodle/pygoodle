"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import error_msg
from pygoodle.format import Format
from pygoodle.git.model import Tag


class LocalTag(Tag):
    """Class encapsulating git tag

    :ivar str name: Branch
    :ivar str formatted_ref: Formatted ref
    """

    @property
    def sha(self) -> str:
        """Commit sha"""
        return offline.get_tag_commit_sha(self.path, self.name)

    def create(self) -> None:
        if self.exists:
            CONSOLE.stdout(f' - Local tag {Format.Git.ref(self.name)} already exists')
            return
        raise NotImplementedError

    @error_msg('Failed to delete local tag')
    def delete(self) -> None:
        if not self.exists:
            CONSOLE.stdout(f" - Local tag {Format.Git.ref(self.short_ref)} doesn't exist")
            return
        CONSOLE.stdout(f' - Delete local tag {Format.Git.ref(self.short_ref)}')
        offline.delete_local_tag(self.path, name=self.name)

    @property
    def exists(self) -> bool:
        return factory.has_local_tag(self.path, self.name)
