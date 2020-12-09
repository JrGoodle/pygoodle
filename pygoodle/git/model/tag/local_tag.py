"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import pygoodle.git.offline as offline

from . import Tag


class LocalTag(Tag):
    """Class encapsulating git tag

    :ivar str name: Branch
    :ivar str formatted_ref: Formatted ref
    """

    def create(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        offline.delete_local_tag(self.path, name=self.name)

    @property
    def exists(self) -> bool:
        return offline.has_local_tag(self.path, tag=self.name)
