"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

import pygoodle.git.offline as offline
from pygoodle.console import CONSOLE
from pygoodle.git.model import Ref


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

    def __eq__(self, other) -> bool:
        if isinstance(other, Tag):
            return self.name == other.name and self.path == other.path
        return False

    @property
    def sha(self) -> str:
        """Commit sha"""
        raise NotImplementedError

    @property
    def short_ref(self) -> str:
        """Short git ref"""

        return self.truncate_ref(self.name)

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        return self.format_git_tag(self.name)

    def checkout(self, check: bool = True) -> None:
        current_commit = offline.current_head_commit_sha(self.path)
        if current_commit == self.sha:
            CONSOLE.stdout(' - On correct commit for tag')
            return
        CONSOLE.stdout(f' - Checkout tag {self.name}')
        super().checkout(check=check)
