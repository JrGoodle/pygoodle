"""pygoodle formatting utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Any, List

import humanize


class Format(object):

    @classmethod
    def bold(cls, output: Any) -> str:
        return f'[bold]{output}[/bold]'

    @classmethod
    def bool(cls, output: bool) -> str:
        if output:
            return Format.green(output)
        else:
            return Format.red(output)

    @classmethod
    def cyan(cls, output: Any) -> str:
        return f'[cyan]{output}[/cyan]'

    @classmethod
    def blue(cls, output: Any) -> str:
        return f'[blue]{output}[/blue]'

    @classmethod
    def green(cls, output: Any) -> str:
        return f'[green]{output}[/green]'

    @classmethod
    def red(cls, output: Any) -> str:
        return f'[red]{output}[/red]'

    @classmethod
    def magenta(cls, output: Any) -> str:
        return f'[magenta]{output}[/magenta]'

    @classmethod
    def yellow(cls, output: Any) -> str:
        return f'[yellow]{output}[/yellow]'

    @classmethod
    def escape(cls, output: Any) -> str:
        import rich.markup as markup
        return markup.escape(str(output))

    @classmethod
    def size(cls, self, size: int) -> str:
        parts = humanize.naturalsize(size).split()
        assert len(parts) == 2
        number = self.bold(parts[0])
        unit = parts[1]
        return FORMAT.green(f'{number} {unit}')

    @classmethod
    def underline(cls, output: Any) -> str:
        return f'[underline]{output}[/underline]'

    @classmethod
    def separator(cls, message: str, character: str) -> str:
        sep = character * len(message)
        return f'[default bold]{sep}[/default bold]'

    @classmethod
    def h1(cls, message: str, newline: bool = True) -> str:
        output = '\n' if newline else ''
        output = f'{output}[default bold]{message}[/default bold]'
        sep = Format.separator(message, '=')
        return f'{output}\n{sep}'

    @classmethod
    def h2(cls, message: str, newline: bool = True) -> str:
        output = '\n' if newline else ''
        output = f'{output}[default bold]{message}[/default bold]'
        sep = Format.separator(message, '-')
        return f'{output}\n{sep}'

    @classmethod
    def h3(cls, message: str, newline: bool = True) -> str:
        output = '\n' if newline else ''
        return f'{output}[default bold underline]# {message}[/default bold underline]'

    @classmethod
    def h4(cls, message: str, newline: bool = True) -> str:
        output = '\n' if newline else ''
        return f'{output}[default bold underline]## {message}[/default bold underline]'

    @classmethod
    def h5(cls, message: str, newline: bool = True) -> str:
        output = '\n' if newline else ''
        return f'{output}[default bold underline]### {message}[/default bold underline]'

    @classmethod
    def gnu_size(cls, size: int) -> str:
        return humanize.naturalsize(size, gnu=True)


FORMAT: Format = Format()


def get_lines(path: Path) -> List[str]:
    contents = path.read_text().splitlines()
    lines = [line.strip() for line in contents]
    return lines
