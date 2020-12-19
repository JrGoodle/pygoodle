"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

from .ref import Ref


class Commit(Ref):
    """Class encapsulating git commit

    :ivar Path path: Path to git repo
    :ivar str sha: Git commit sha
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path, sha: str):
        """GitRepo __init__

        :param Path path: Path to git repo
        :param str sha: Full git commit sha
        """

        super().__init__(path)
        self._sha: str = sha

    def __eq__(self, other) -> bool:
        if isinstance(other, Commit):
            return super().__eq__(other) and self.path == other.path
        return False

    @property
    def sha(self) -> str:
        """Commit sha"""
        return self._sha

    @property
    def short_ref(self) -> str:
        """Short git ref"""

        return self.sha

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.sha