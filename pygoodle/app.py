"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import argparse
import pkg_resources
from subprocess import CalledProcessError
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import argcomplete
from trio import MultiError

from pygoodle.console import CONSOLE


class Argument(object):

    def __init__(self, *args, **kwargs):
        self.args: Tuple[Any] = args
        self.options: Dict[str, Any] = kwargs


Parser = Union[argparse.ArgumentParser, argparse._MutuallyExclusiveGroup, argparse._ArgumentGroup]  # noqa


class Subcommand(object):

    name: str = 'subcommand'
    help: str = f'{name} help'
    args: List[Argument] = []
    mutually_exclusive_args: List[List[Argument]] = []
    argument_groups: Dict[str, List[Argument]] = {}
    subcommands: List['Subcommand'] = []

    def __init__(self):
        self._parser: Optional[argparse.ArgumentParser] = None

    @staticmethod
    def run(args) -> None:
        raise NotImplementedError

    def print_help(self) -> None:
        self._parser.print_help()

    def add_parser(self, parser) -> None:
        self._parser = parser


class App(object):

    def __init__(self, name: str, entry_point: Optional[str] = None,
                 arguments: Optional[List[Argument]] = None,
                 mutually_exclusive_args: Optional[List[List[Argument]]] = None,
                 subcommands: Optional[List[Subcommand]] = None,
                 argument_groups: Optional[Dict[str, List[Argument]]] = None):
        from rich.traceback import install
        install()
        import colorama
        colorama.init()

        self.name = name
        self.entry_point = name if entry_point is None else entry_point
        self.parser: argparse.ArgumentParser = self._create_parser(arguments, mutually_exclusive_args, argument_groups)
        self.subparsers = self.parser.add_subparsers(dest=f'{self.entry_point} subcommand')
        for subcommand in subcommands:
            self._add_subcommand(subcommand)

    def run(self, process_args: Callable = lambda _: None) -> None:
        """command CLI main function"""

        try:
            argcomplete.autocomplete(self.parser)
            args = self.parser.parse_args()
            process_args(args)
            args.func(args)
        except CalledProcessError as err:
            CONSOLE.stderr('** CalledProcessError **')
            CONSOLE.stderr(err)
            exit(err.returncode)
        except MultiError as err:
            CONSOLE.stderr('** MultiError **')
            CONSOLE.stderr(err.exceptions)
            exit(1)
        except OSError as err:
            CONSOLE.stderr('** OSError **')
            CONSOLE.stderr(err)
            exit(err.errno)
        except SystemExit as err:
            if err.code == 0:
                exit()
            CONSOLE.stderr('** SystemExit **')
            CONSOLE.print_exception()
            exit(err.code)
        except KeyboardInterrupt:
            CONSOLE.stderr('** KeyboardInterrupt **')
            exit(1)
        except BaseException:  # noqa
            CONSOLE.stderr('** Unhandled exception **')
            CONSOLE.print_exception()
            exit(1)

    @staticmethod
    def _add_parser_arguments(parser: Parser, arguments: List[Argument]) -> None:
        """Add arguments to parser

        :param Parser parser: Parser to add arguments to
        :param Arguments arguments: Arguments to add to parser
        """

        for argument in arguments:
            parser.add_argument(*argument.args, **argument.options)

    def _add_subcommand(self, subcommand: Subcommand, subparsers: Optional[argparse._SubParsersAction] = None) -> None:  # noqa
        """Add arguments to parser

        :param Subcommand subcommand: Subcommand object
        :param Optional subparsers: Parser to add subcommand to
        """

        subparsers = self.subparsers if subparsers is None else subparsers
        parser = subparsers.add_parser(subcommand.name, help=subcommand.help)
        subcommand.add_parser(parser)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.set_defaults(func=subcommand.run)

        self._add_parser_arguments(parser, subcommand.args)

        for args in subcommand.mutually_exclusive_args:
            self._add_parser_arguments(parser.add_mutually_exclusive_group(), args)

        for title, args in subcommand.argument_groups.items():
            self._add_parser_arguments(parser.add_argument_group(title=title), args)

        if subcommand.subcommands:
            command_subparsers = parser.add_subparsers(dest=f'{subcommand.name} subcommand', help=subcommand.help)
            for command in subcommand.subcommands:
                self._add_subcommand(command, command_subparsers)

    def _create_parser(self, args: Optional[List[Argument]] = None,
                       mutually_exclusive_args: Optional[List[List[Argument]]] = None,
                       argument_groups: Optional[Dict[str, List[Argument]]] = None) -> argparse.ArgumentParser:
        """Configure CLI parsers

        :return: Configured argument parser for command
        :rtype: argparse.ArgumentParser
        """

        try:
            command_parser = argparse.ArgumentParser(prog=self.entry_point)
            command_parser.set_defaults(func=command_parser.print_help)
            version_message = f"{self.entry_point} version {pkg_resources.require(self.name)[0].version}"
            self._add_parser_arguments(command_parser, [
                Argument('-v', '--version', action='version', version=version_message)
            ])

            if args is not None:
                self._add_parser_arguments(command_parser, args)

            if mutually_exclusive_args is not None:
                for args in mutually_exclusive_args:
                    self._add_parser_arguments(command_parser.add_mutually_exclusive_group(), args)

            if argument_groups is not None:
                for title, args in argument_groups.items():
                    self._add_parser_arguments(command_parser.add_argument_group(title=title), args)

            return command_parser
        except Exception:
            CONSOLE.stderr('Failed to create parser')
            raise
