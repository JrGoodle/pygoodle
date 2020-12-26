"""Clowder command line utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import Optional

import jsonschema
import yaml as pyyaml

import pygoodle.filesystem as fs
from pygoodle.console import CONSOLE
from .error import ExistingFileError
from .format import Format

YAML: str = '.yaml'
YML: str = '.yml'


class InvalidYamlError(Exception):
    pass


class MissingYamlError(Exception):
    pass


class Yaml:

    def __init__(self, path: Path, schema: Optional[str] = None):
        if path.suffix != YAML and path.suffix != YML:
            path = path / YML
        self.path: Path = path
        self.schema: Optional[str] = schema

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    @property
    def path_with_alternate_extension(self) -> Path:
        if self.has_yaml_extension:
            return self.path_with_yml_extension
        else:
            return self.path_with_yaml_extension

    @property
    def alternate_extension_exists(self) -> bool:
        return self.path_with_alternate_extension.is_file()

    @property
    def has_yaml_extension(self) -> bool:
        return self.path.suffix == YAML

    @property
    def has_yml_extension(self) -> bool:
        return self.path.suffix == YML

    @property
    def path_with_yaml_extension(self) -> Path:
        if self.has_yaml_extension:
            return self.path
        return self.path.parent / f'{self.path.stem}{YAML}'

    @property
    def path_with_yml_extension(self) -> Path:
        if self.has_yml_extension:
            return self.path
        return self.path.parent / f'{self.path.stem}{YML}'

    def delete(self, alternate_extension: bool = False):
        if not alternate_extension:
            fs.remove(self.path)
            return

        if self.has_yaml_extension:
            fs.remove(self.path_with_yml_extension)
        else:
            fs.remove(self.path_with_yaml_extension)

    def load(self, relative_to: Optional[Path] = None) -> dict:
        """Load clowder config from yaml file

        :param Optional[Path] relative_to: Directory yaml file is relative to
        :return: YAML python object
        :raise InvalidYamlError:
        """

        try:
            with self.path.open() as raw_file:
                parsed_yaml = pyyaml.safe_load(raw_file)
                if parsed_yaml is None:
                    raise InvalidYamlError(f"No entries in {Format.path(self.path, relative_to=relative_to)}")
                return parsed_yaml
        except pyyaml.YAMLError:
            # LOG.error(f"Failed to open file '{yaml_file}'")
            raise

    def save(self, contents: dict) -> None:
        """Save yaml file to disk

        :param dict contents: Parsed YAML python object
        :raise ExistingFileError:
        """

        if self.path.is_file():
            raise ExistingFileError(f"File already exists: {Format.path(self.path)}")

        CONSOLE.stdout(f" - Save yaml to file at {Format.path(self.path)}")
        try:
            with self.path.open(mode="w") as raw_file:
                pyyaml.safe_dump(contents, raw_file, default_flow_style=False, indent=2, sort_keys=False)
        except pyyaml.YAMLError:
            # LOG.error(f"Failed to save file {Format.path(yaml_file)}")
            raise

    def validate(self, schema: Optional[str] = None, relative_to: Optional[Path] = None) -> dict:
        """Validate yaml file

        :param str schema: json schema
        :param Optional[Path] relative_to: Path to load relative to
        :return: Parsed YAML python object
        """

        schema = self.schema if schema is None else schema
        try:
            schema = pyyaml.safe_load(schema)
            parsed = self.load(relative_to=relative_to)
            jsonschema.validate(parsed, schema)
            return parsed
        except jsonschema.exceptions.ValidationError:
            # LOG.error(f'Yaml json schema validation failed {Format.invalid_yaml(file_path.name)}\n')
            raise

    @staticmethod
    def get_string(dictionary: dict) -> str:
        """Return yaml string from python data structures

        :param dict dictionary: YAML python object
        :return: YAML as a string
        """

        try:
            return pyyaml.safe_dump(dictionary, default_flow_style=False, indent=2, sort_keys=False).strip()
        except pyyaml.YAMLError:
            # LOG.error(f"Failed to dump yaml file contents",)
            raise

    def update_extension(self) -> Optional[Path]:
        if self.path_with_yml_extension.exists():
            self.path = self.path_with_yml_extension
        elif self.path_with_yaml_extension.exists():
            self.path = self.path_with_yaml_extension
        return self.path
