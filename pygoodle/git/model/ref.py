"""clowder ref enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

import pygoodle.git.offline as offline


class Ref:
    """Class encapsulating git ref

    :ivar Path path: Path to git repo
    :ivar str formatted_ref: Formatted ref
    """

    def __init__(self, path: Path):
        """Ref __init__

        :param Path path: Path to git repo
        """

        self.path: Path = path
        self.check_ref_format(self.formatted_ref)

    @property
    def short_ref(self) -> str:
        """Short git ref"""
        raise NotImplementedError

    @property
    def formatted_ref(self) -> str:
        """Formatted git ref"""

        raise NotImplementedError

    @staticmethod
    def truncate_ref(ref: str) -> str:
        """Return bare branch, tag, or sha

        :param str ref: Full pathspec or short ref
        :return: Ref with 'refs/heads/' and 'refs/tags/' prefix removed
        """

        git_branch = "refs/heads/"
        git_tag = "refs/tags/"
        if ref.startswith(git_branch):
            length = len(git_branch)
        elif ref.startswith(git_tag):
            length = len(git_tag)
        else:
            length = 0
        return ref[length:]

    @staticmethod
    def check_ref_format(ref: str) -> bool:
        """Check if git ref is correctly formatted

        :param str ref: Git ref
        :return: True, if git ref is a valid format
        """

        return offline.check_ref_format(ref)

    @staticmethod
    def format_git_branch(branch: str) -> str:
        """Returns properly formatted git branch

        :param str branch: Git branch name
        :return: Branch prefixed with 'refs/heads/'
        """

        prefix = "refs/heads/"
        return branch if branch.startswith(prefix) else f"{prefix}{branch}"

    @staticmethod
    def format_git_tag(tag: str) -> str:
        """Returns properly formatted git tag

        :param str tag: Git tag name
        :return: Tag prefixed with 'refs/heads/'
        """

        prefix = "refs/tags/"
        return tag if tag.startswith(prefix) else f"{prefix}{tag}"

    def checkout(self) -> None:
        offline.checkout(self.path, ref=self.short_ref)
