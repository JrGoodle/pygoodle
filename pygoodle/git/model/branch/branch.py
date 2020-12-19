"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

from .. import Ref


class Branch(Ref):
    """Class encapsulating git branch

    :ivar Path path: Path to git repo
    :ivar str name: Branch name
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, name: str):
        """Branch __init__

        :param Path path: Path to git repo
        :param str name: Branch name
        """

        super().__init__(path)
        self.name: str = name

    def __eq__(self, other) -> bool:
        if isinstance(other, Branch):
            return super().__eq__(other) and self.name == other.name
        return False

    @property
    def sha(self) -> Optional[str]:
        """Commit sha"""
        raise NotImplementedError

    @property
    def short_ref(self) -> str:
        """Short git ref"""

        return self.truncate_ref(self.name)

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.format_git_branch(self.name)
