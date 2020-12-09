"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

from .. import Ref


class Tag(Ref):
    """Class encapsulating git tag

    :ivar Path path: Path to git repo
    :ivar str name: Branch
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str):
        """GitRepo __init__

        :param Path path: Path to git repo
        :param str name: Tag name
        """

        super().__init__(path)
        self.name: str = name

    @property
    def short_ref(self) -> str:
        """Short git ref"""

        return self.truncate_ref(self.name)

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.format_git_tag(self.name)
