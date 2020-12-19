"""git model factory

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.git.constants import FETCH_URL, PUSH_URL
from pygoodle.git.model import (
    LocalBranch,
    LocalTag,
    Remote,
    RemoteBranch,
    RemoteTag,
    Submodule,
    TrackingBranch
)


def get_remotes(path: Path) -> List[Remote]:
    remotes = offline.get_remotes_info(path)
    return [Remote(path, name, fetch_url=values[FETCH_URL], push_url=values[PUSH_URL])
            for name, values in remotes.items()]


def get_remote(path: Path, name: str) -> Optional[Remote]:
    remotes = get_remotes(path)
    remote = [r for r in remotes if r.name == name]
    return remote[0] if remote else None


def get_local_branches(path: Path) -> List[LocalBranch]:
    branches = offline.get_local_branches_info(path)
    return [LocalBranch(path, branch) for branch in branches]


def get_local_tags(path: Path) -> List[LocalTag]:
    tags = offline.get_local_tags_info(path)
    return [LocalTag(path, tag) for tag in tags]


def get_submodules(path: Path) -> List[Submodule]:
    submodules_info = offline.get_submodules_info(path)
    submodules = []
    for key in submodules_info.keys():
        submodule_info = submodules_info[key]
        url = submodule_info['url']
        submodule_path = Path(submodule_info['path'])
        branch = submodule_info['branch'] if 'branch' in submodule_info else None
        active = submodule_info['active'] if 'active' in submodule_info else None
        active = True if active == 'true' else False
        submodule_commit = offline.get_submodule_commit(path, submodule_path)
        submodule = Submodule(path, submodule_path, url=url, commit=submodule_commit, branch=branch, active=active)
        submodules.append(submodule)
    return submodules


def get_tracking_branches(path: Path) -> List[TrackingBranch]:
    branches = offline.get_tracking_branches_info(path)
    tracking_branches = []
    for local_branch, info in branches.items():
        upstream_remote = get_remote(path, info['upstream_remote'])
        upstream_branch = RemoteBranch(info['upstream_branch'], upstream_remote)
        push_remote = get_remote(path, info['push_remote'])
        push_branch = RemoteBranch(info['push_branch'], push_remote)
        tracking_branch = TrackingBranch(path, local_branch,
                                         upstream_branch=upstream_branch,
                                         push_branch=push_branch)
        tracking_branches.append(tracking_branch)
    return tracking_branches


def get_remote_branches(remote: Remote) -> List[RemoteBranch]:
    branches, default_branch = offline.get_remote_branches_info(remote.path, remote.name)
    branches = [RemoteBranch(branch, remote) for branch in branches]
    if default_branch is not None:
        branches.append(RemoteBranch(default_branch, remote, is_default=True))
    return branches


def get_remote_tags(remote: Remote) -> List[RemoteTag]:
    tags = online.get_remote_tags_info(remote.path, remote.name)
    return [RemoteTag(tag, remote) for tag in tags]
