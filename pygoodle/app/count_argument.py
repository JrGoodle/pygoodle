"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from .argument import Argument


class CountArgument(Argument):

    def __init__(self, *args, **kwargs):
        super().__init__(
            metavar='<n>',
            nargs=1,
            default=None,
            type=int,
            *args, **kwargs
        )
