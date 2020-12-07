"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Any, Dict, Tuple

from ..format import Format


class Argument(object):

    def __init__(self, *args, **kwargs):
        self.args: Tuple[Any] = args
        metavar = 'metavar'
        if metavar not in kwargs:
            name = self._get_name(args)
            kwargs[metavar] = f'<{name}>'
        self.options: Dict[str, Any] = kwargs

    @staticmethod
    def _get_name(args: Tuple[Any]) -> str:
        names = [a for a in args if a.beginswith('--')]
        if names:
            return Format.remove_prefix(names[0], '--')

        names = [a for a in args if a.beginswith('-')]
        if names:
            return Format.remove_prefix(names[0], '-')

        names = [a for a in args if not a.beginswith('-')]
        if names:
            return names[0]

        raise Exception('Failed to infer argument name')
