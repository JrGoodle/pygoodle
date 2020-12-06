"""error

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""


class ExistingFileError(Exception):
    pass


class ExistingSymlinkError(Exception):
    pass


class MissingFileError(Exception):
    pass


class MissingYamlError(Exception):
    pass


class UnknownArgumentError(Exception):
    pass
