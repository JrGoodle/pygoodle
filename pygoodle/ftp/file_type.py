"""file type enum

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from enum import auto, unique

from .formatting import FORMAT
from .enum import AutoLowerName


@unique
class FileType(AutoLowerName):
    FILE = auto()
    DIR = auto()

    @property
    def formatted_value(self) -> str:
        if self is FileType.DIR:
            return FORMAT.blue(self.value)
        elif self is FileType.FILE:
            return self.value
        else:
            raise Exception('Unknown file type')
