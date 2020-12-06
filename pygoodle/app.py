"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import argparse
import pkg_resources
from subprocess import CalledProcessError
from typing import Callable, List, Optional, Tuple, Union

import argcomplete
import colorama
from trio import MultiError

from pygoodle.console import CONSOLE


Parser = Union[argparse.ArgumentParser, argparse._MutuallyExclusiveGroup, argparse._ArgumentGroup]  # noqa
Arguments = List[Tuple[List[str], dict]]


class Subcommand(object):

    def __init__(self, name: str, help_message: str, args: Optional[Arguments] = None,
                 mutually_exclusive_args: Optional[List[Arguments]] = None,
                 subcommands: Optional[List['Subcommand']] = None):
        self.name: str = name
        self.help_message: str = help_message
        self.args: Optional[Arguments] = args
        self.mutually_exclusive_args: Optional[List[Arguments]] = mutually_exclusive_args
        self.subcommands: Optional[List[Subcommand]] = subcommands

    def run(self, args) -> None:
        raise NotImplementedError


class App(object):

    def __init__(self, name: str, entry_point: Optional[str] = None,
                 arguments: Optional[Arguments] = None,
                 mutually_exclusive_args: Optional[List[Arguments]] = None,
                 subcommands: Optional[List[Subcommand]] = None):
        from rich.traceback import install
        install()
        colorama.init()

        self.name = name
        self.entry_point = name if entry_point is None else entry_point
        self.parser: argparse.ArgumentParser = self._create_parser(arguments, mutually_exclusive_args)
        self.subparsers = self.parser.add_subparsers(dest='subcommand')
        for subcommand in subcommands:
            self.add_subcommand(subcommand)

    def add_subcommand(self, subcommand: Subcommand, parser: Optional[Parser] = None) -> None:
        """Add arguments to parser

        :param Subcommand subcommand: Subcommand object
        :param Optional[Parser] parser: Parser to add subcommand to
        """

        parser = self.subparsers if parser is None else parser
        sub_parser = parser.add_parser(subcommand.name, help=subcommand.help_message)
        sub_parser.formatter_class = argparse.RawTextHelpFormatter

        if subcommand.args is not None:
            self._add_parser_arguments(sub_parser, subcommand.args)

        if subcommand.mutually_exclusive_args is not None:
            for args in subcommand.mutually_exclusive_args:
                self._add_parser_arguments(sub_parser.add_mutually_exclusive_group(), args)

        if subcommand.subcommands is None:
            sub_parser.set_defaults(func=sub_parser.print_help)
        else:
            sub_parser.set_defaults(func=subcommand.run)
            for command in subcommand.subcommands:
                self.add_subcommand(command, sub_parser)

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
    def _add_parser_arguments(parser: Parser, arguments: Arguments) -> None:
        """Add arguments to parser

        :param Parser parser: Parser to add arguments to
        :param Arguments arguments: Arguments to add to parser
        """

        for argument in arguments:
            parser.add_argument(*argument[0], **argument[1])

    def _create_parser(self, arguments: Optional[Arguments] = None,
                       mutually_exclusive_args: Optional[List[Arguments]] = None) -> argparse.ArgumentParser:
        """Configure CLI parsers

        :return: Configured argument parser for command
        :rtype: argparse.ArgumentParser
        """

        try:
            command_parser = argparse.ArgumentParser(prog=self.entry_point)
            command_parser.set_defaults(func=command_parser.print_help)
            version_message = f"{self.entry_point} version {pkg_resources.require(self.name)[0].version}"
            self._add_parser_arguments(command_parser, [
                (['-v', '--version'], dict(action='version', version=version_message))
            ])

            if arguments is not None:
                self._add_parser_arguments(command_parser, arguments)

            if mutually_exclusive_args is not None:
                for args in mutually_exclusive_args:
                    self._add_parser_arguments(command_parser.add_mutually_exclusive_group(), args)

            return command_parser
        except Exception:
            CONSOLE.stderr('Failed to create parser')
            raise
