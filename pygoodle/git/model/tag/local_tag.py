"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.model.factory as factory
import pygoodle.git.offline as offline
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
        raise NotImplementedError

    def delete(self) -> None:
        offline.delete_local_tag(self.path, name=self.name)

    @property
    def exists(self) -> bool:
        tags = factory.get_local_tags(self.path)
        return any([tag == self for tag in tags])
