"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import argparse
import pkg_resources
from subprocess import CalledProcessError

import argcomplete
import colorama
from trio import MultiError

from pygoodle.cli import add_parser_arguments
from pygoodle.console import CONSOLE


class App(object):

    def __init__(self, name: str):
        from rich.traceback import install
        install()
        colorama.init()

        self.name = name
        self.parser: argparse.ArgumentParser = self._create_parser()
        self.subparsers = self.parser.add_subparsers(dest='subcommand')

    def _create_parser(self) -> argparse.ArgumentParser:
        """Configure CLI parsers

        :return: Configured argument parser for command
        :rtype: argparse.ArgumentParser
        """

        def command_help(_):
            """command help handler"""

            command_parser.print_help()

        try:
            command_parser = argparse.ArgumentParser(prog=self.name)
            command_parser.set_defaults(func=command_help)
            version_message = f"{self.name} version {pkg_resources.require(self.name)[0].version}"
            add_parser_arguments(command_parser, [
                (['-v', '--version'], dict(action='version', version=version_message))
            ])

            return command_parser
        except Exception:
            CONSOLE.stderr('Failed to create parser')
            raise

    def run(self) -> None:
        """command CLI main function"""

        try:
            argcomplete.autocomplete(self.parser)
            args = self.parser.parse_args()
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
