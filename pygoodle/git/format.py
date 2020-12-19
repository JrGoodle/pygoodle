"""formatting utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Any

from pygoodle.format import Format


class GitFormat(Format):

    @classmethod
    def ref(cls, output: Any) -> str:
        return cls.magenta(output)

    @classmethod
    def remote(cls, output: Any) -> str:
        return cls.yellow(output)

    @classmethod
    def upstream(cls, output: Any) -> str:
        return cls.cyan(output)

    @classmethod
    def url(cls, output: any) -> str:
        return cls.cyan(output)
