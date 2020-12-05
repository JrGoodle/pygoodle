"""pygoodle plex utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Dict

from pygoodle.environment import ENVIRONMENT

from .console import CONSOLE
from .execute import run_command


class Plex(object):

    def __init__(self):
        sections = self._get_section_ids()
        self.movies_section_id: int = sections['Movies']
        self.tv_section_id: int = sections['TV Shows']

    def update_library(self) -> None:
        CONSOLE.stdout('Update Plex library')
        CONSOLE.stdout('Update Movies')
        self._update_section(self.movies_section_id)
        CONSOLE.stdout('Update TV Shows')
        self._update_section(self.tv_section_id)

    @staticmethod
    def _get_section_ids() -> Dict[str, int]:
        command = f"'{ENVIRONMENT.plex_media_scanner}' --list"
        results = run_command(command, print_output=False)
        output: str = results.stdout
        lines = [line.split(':') for line in output.splitlines() if line]
        sections = {name.strip(): int(section.strip()) for section, name in lines}
        return sections

    @staticmethod
    def _update_section(section: int) -> None:
        command = f"'{ENVIRONMENT.plex_media_scanner}' --scan --refresh --section {section}"
        run_command(command)
