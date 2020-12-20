"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
from pygoodle.console import CONSOLE
from pygoodle.git.decorators import error_msg
from pygoodle.git.format import GitFormat
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
            CONSOLE.stdout(f' - Local tag {GitFormat.ref(self.name)} already exists')
            return
        raise NotImplementedError

    @error_msg('Failed to delete local tag')
    def delete(self) -> None:
        # TODO: Check if tag exists
        CONSOLE.stdout(f' - Delete local tag {GitFormat.ref(self.short_ref)}')
        offline.delete_local_tag(self.path, name=self.name)

    @property
    def exists(self) -> bool:
        tags = factory.get_local_tags(self.path)
        return any([tag == self for tag in tags])
