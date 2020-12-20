"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import pygoodle.git.offline as offline
from pygoodle.console import CONSOLE
from pygoodle.git.model import Ref
from pygoodle.format import Format


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

    def delete(self) -> None:
        raise NotImplementedError

    @property
    def is_tracking_branch(self) -> bool:
        raise NotImplementedError

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

    def checkout(self, check: bool = True) -> None:
        current_branch = offline.current_branch(self.path)
        if current_branch == self.name:
            CONSOLE.stdout(f' - Branch {Format.magenta(self.short_ref)} already checked out')
            return
        CONSOLE.stdout(f' - Checkout branch {Format.magenta(self.short_ref)}')
        super().checkout(check=check)
