"""Clowder command line utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path

import jsonschema
import yaml as pyyaml

from .error import ExistingFileError
from .format import Format


class InvalidYamlError(Exception):
    pass


class MissingYamlError(Exception):
    pass


def load_yaml_file(yaml_file: Path, relative_dir: Path) -> dict:
    """Load clowder config from yaml file

    :param Path yaml_file: Path of yaml file to load
    :param Path relative_dir: Directory yaml file is relative to
    :return: YAML python object
    :raise InvalidYamlError:
    """

    try:
        with yaml_file.open() as raw_file:
            parsed_yaml = pyyaml.safe_load(raw_file)
            if parsed_yaml is None:
                config_yaml = yaml_file.relative_to(relative_dir)
                raise InvalidYamlError(f"{Format.path(yaml_file)}\nNo entries in {Format.path(config_yaml)}")
            return parsed_yaml
    except pyyaml.YAMLError:
        # LOG.error(f"Failed to open file '{yaml_file}'")
        raise


def save_yaml_file(yaml_output: dict, yaml_file: Path) -> None:
    """Save yaml file to disk

    :param dict yaml_output: Parsed YAML python object
    :param Path yaml_file: Path to save yaml file
    :raise ExistingFileError:
    """

    if yaml_file.is_file():
        raise ExistingFileError(f"File already exists: {Format.path(yaml_file)}")

    # CONSOLE.stdout(f" - Save yaml to file at {Format.path(yaml_file)}")
    try:
        with yaml_file.open(mode="w") as raw_file:
            pyyaml.safe_dump(yaml_output, raw_file, default_flow_style=False, indent=2, sort_keys=False)
    except pyyaml.YAMLError:
        # LOG.error(f"Failed to save file {Format.path(yaml_file)}")
        raise


def validate_yaml_file(parsed_yaml: dict, schema: str) -> None:
    """Validate yaml file

    :param dict parsed_yaml: Parsed yaml dictionary
    :param str schema: json schema
    """

    json_schema = _load_json_schema(schema)
    try:
        jsonschema.validate(parsed_yaml, json_schema)
    except jsonschema.exceptions.ValidationError:
        # LOG.error(f'Yaml json schema validation failed {Format.invalid_yaml(file_path.name)}\n')
        raise


def yaml_string(dictionary: dict) -> str:
    """Return yaml string from python data structures

    :param dict dictionary: YAML python object
    :return: YAML as a string
    """

    try:
        return pyyaml.safe_dump(dictionary, default_flow_style=False, indent=2, sort_keys=False)
    except pyyaml.YAMLError:
        # LOG.error(f"Failed to dump yaml file contents",)
        raise


def _load_json_schema(schema: str) -> dict:
    """Return json schema file

    :param str schema: File prefix for json schema
    :return: Loaded json dict
    """

    return pyyaml.safe_load(schema)
