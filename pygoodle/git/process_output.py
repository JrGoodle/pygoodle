"""Misc git utils"""

from typing import Dict, List, Optional, Tuple

from pygoodle.format import Format
from . import FETCH_URL, PUSH_URL

# TODO: Update to use ConfigParser


def tag_shas(output: str) -> Dict[str, str]:
    # TODO: Add expected output example
    return shas(output, 'refs/tags/')


def branch_shas(output: str) -> Dict[str, str]:
    # TODO: Add expected output example
    return shas(output, 'refs/heads/')


def shas(output: str, prefix: str) -> Dict[str, str]:
    # TODO: Add expected output example
    lines = output.strip().splitlines()
    items = {}
    for line in lines:
        components = line.split()
        sha = components[0].strip()
        name = Format.remove_prefix(components[1], prefix)
        items[name] = sha
    return items


def tracking_branches(output: str) -> Tuple[Optional[str], str]:
    # Expected output format:
    # > git rev-parse --symbolic-full-name git-old@{upstream}
    # refs/heads/git
    # > git rev-parse --symbolic-full-name git-old@{upstream}
    # refs/remotes/origin/git
    if output.startswith('refs/heads'):
        remote = None
        branch = Format.remove_prefix('refs/heads', output)
    elif output.startswith('refs/remotes'):
        components = Format.remove_prefix('refs/remotes', output).split('/')
        remote = components[2]
        branch = components[3]
    else:
        raise Exception('Failed to parse tracking branch output')
    return remote, branch


def remote_branches(output: str, remote: str) -> Tuple[Optional[str], List[str]]:
    # TODO: Add expected output example
    lines = output.strip().splitlines()
    items = []
    default_branch = None
    for line in lines:
        components = line.split()
        if len(components) == 1:
            name = Format.remove_prefix(components[0].strip(), f'{remote}/')
            items.append(name)
        elif len(components) == 3 and components[1] == '->':
            name = Format.remove_prefix(components[2].strip(), f'{remote}/')
            default_branch = name
        else:
            raise Exception('Wrong number of components for remote branch')
    return default_branch, items


def remotes(output: str) -> Dict[str, Dict[str, str]]:
    # Expected output format:
    # origin	git@github.com:JrGoodle/pygoodle.git (fetch)
    # origin	git@github.com:JrGoodle/pygoodle.git (push)
    lines = output.splitlines()
    line = [line.split() for line in lines]
    _remotes = {}
    for components in line:
        name = components[0].strip()
        url = components[1].strip()
        kind = components[2].strip()
        if kind == '(fetch)':
            _remotes[name][FETCH_URL] = url
        elif kind == '(push)':
            _remotes[name][PUSH_URL] = url
        else:
            raise Exception('Unknown')
    return _remotes


def submodules(output: List[str]) -> Dict[str, Dict[str, str]]:
    # Expected output format for .gitmodules:
    # submodule.path/to/Optional.path path/to/Optional
    # submodule.path/to/Optional.url https://github.com/akrzemi1/Optional.git
    # submodule.path/to/Optional.branch master
    #
    # Expected output format for .git/config:
    # submodule.path/to/Optional.active true
    # submodule.path/to/Optional.url https://github.com/akrzemi1/Optional.git
    _submodules = {}
    for submodule_info in output:
        submodule_info = submodule_info.split()
        value = submodule_info[1]
        components = submodule_info[0].split('.')
        path = components[1]
        key = components[2]
        if path in _submodules.keys():
            _submodules[path][key] = value
        else:
            _submodules[path] = {key: value}
    return _submodules
