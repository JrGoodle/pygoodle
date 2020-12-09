"""formatting utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import re
from pathlib import Path
from typing import Any, List, Optional

import humanize


class Format:

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
    def default(cls, output: Any) -> str:
        return f'[default]{output}[/default]'

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
    def size(cls, size: int) -> str:
        parts = humanize.naturalsize(size).split()
        assert len(parts) == 2
        number = Format.bold(parts[0])
        unit = parts[1]
        return Format.green(f'{number} {unit}')

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

    @classmethod
    def path(cls, path: Path) -> str:
        return Format.cyan(str(path))

    @classmethod
    def _format_yaml_symlink(cls, symlink: Path) -> str:
        """Return formatted string for yaml symlink

        :param Path symlink: Yaml symlink
        :return: Formatted string for yaml symlink
        """

        assert symlink.is_symlink()
        return f"\n{Format.path(symlink)} -> {Format.path(symlink.resolve())}\n"

    @classmethod
    def _format_yaml_file(cls, path: Path, relative_to: Optional[Path]) -> str:
        """Return formatted string for yaml file

        :param Path path: Yaml file path
        :return: Formatted string for yaml file
        """

        if relative_to is not None:
            path = path.resolve().relative_to(relative_to)
        return f"\n{Format.path(path)}\n"

    @classmethod
    def get_lines(cls, path: Path) -> List[str]:
        contents = path.read_text().splitlines()
        lines = [line.strip() for line in contents]
        return lines

    @classmethod
    def list_from_string(cls, text: str, sep: Optional[str] = None) -> List[str]:
        return text.split(sep=sep)

    @classmethod
    def clean_escape_sequences(cls, string: str) -> str:
        reaesc = re.compile(r'\x1b[^m]*m')
        return reaesc.sub('', string)

    @classmethod
    def remove_prefix(cls, text: str, prefix: str) -> str:
        """Remove prefix from string

        :param str text: Text to remove prefix from
        :param str prefix: Prefix to remove
        :return: Text with prefix removed if present
        """

        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    @classmethod
    def remove_suffix(cls, text: str, suffix: str) -> str:
        if text.endswith(suffix):
            return text[:len(suffix)]
        return text
