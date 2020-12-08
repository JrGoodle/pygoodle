"""command line app

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

import argparse
from typing import Dict, List, Optional

import pygoodle.reflection as reflect
from .argument import Argument


class Subcommand(object):

    class Meta:
        name: str = 'subcommand'
        help: str = f'{name} help'
        args: List[Argument] = []
        mutually_exclusive_args: List[List[Argument]] = []
        argument_groups: Dict[str, List[Argument]] = {}
        subcommands: List['Subcommand'] = []

    def __init__(self):
        self._parser: Optional[argparse.ArgumentParser] = None
        self.name: str = 'subcommand'
        self.help: str = f'{self.name} help'
        self.args: List[Argument] = []
        self.mutually_exclusive_args: List[List[Argument]] = []
        self.argument_groups: Dict[str, List[Argument]] = {}
        self.subcommands: List['Subcommand'] = []
        self._update_meta()

    @staticmethod
    def run(args) -> None:
        raise NotImplementedError

    def print_help(self) -> None:
        self._parser.print_help()

    def add_parser(self, parser) -> None:
        self._parser = parser

    def _update_attr(self, name: str, meta: Meta) -> None:
        reflect.update_attr(self, name, meta)

    def _update_meta(self) -> None:
        classes = reflect.method_resolution_order(self, reverse=True)
        for cls in classes:
            meta = reflect.class_member(cls, 'Meta')
            if meta is not None:
                self._update_attr('name', meta)
                self._update_attr('help', meta)
                self._update_attr('args', meta)
                self._update_attr('mutually_exclusive_args', meta)
                self._update_attr('argument_groups', meta)
                self._update_attr('subcommands', meta)
