"""Clowder console utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import sys
from functools import wraps
from io import StringIO
from typing import Any

from rich.console import Console as RichConsole


def disable_output(func):
    """Disable Console output for wrapped function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper"""

        CONSOLE.print_output = False
        try:
            retval = func(*args, **kwargs)
            CONSOLE.print_output = True
            return retval
        except:  # noqa
            CONSOLE.print_output = True
            raise

    return wrapper


class Console:
    """clowder console class"""

    def __init__(self):
        self.print_output: bool = True
        self._stdout: RichConsole = RichConsole(force_terminal=True,
                                                # color_system='256',
                                                width=160)
        self._stderr: RichConsole = RichConsole(file=sys.stderr,
                                                force_terminal=True,
                                                # color_system='256',
                                                width=160)
        self._stringio: RichConsole = RichConsole(file=StringIO(),
                                                  width=160)

    @property
    def stdout_console(self) -> RichConsole:
        return self._stdout

    def stderr(self, output: Any = '', force: bool = False) -> None:
        if self.print_output or force:
            self._stderr.log(output, log_locals=True)

    def stdout(self, output: Any = '', force: bool = False) -> None:
        if self.print_output or force:
            self._stdout.print(output)

    def print_exception(self, force: bool = False) -> None:
        if self.print_output or force:
            self._stderr.print_exception()

    def delete_lines(self, count: int = 1, force: bool = False) -> None:
        if self.print_output or force:
            for _ in range(count):
                print('\033[A                             \033[A')

    @property
    def width(self) -> int:
        width = self._stdout.width
        return width

    @staticmethod
    def _debug_console(console: RichConsole) -> None:
        print(console.encoding)
        print(console.color_system)
        print(console.width)
        print(console.is_terminal)
        print(console.is_dumb_terminal)

    def _pretty_log_message(self, output: Any) -> str:
        self._stringio.print(output)
        output = self._stringio.file.getvalue()
        return output

    @property
    def _pretty_traceback(self) -> str:
        self._stringio.print_exception()
        output = self._stringio.file.getvalue()
        return output


CONSOLE: Console = Console()
