"""git model factory

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional, Tuple

import pygoodle.git.offline as offline
import pygoodle.git.online as online
from pygoodle.git.model import (
    LocalBranch,
    LocalTag,
    Remote,
    RemoteBranch,
    RemoteTag,
    Submodule,
    TrackingBranch
)


class AllBranches:

    def __init__(self, local_branches: List[LocalBranch], remote_branches: List[RemoteBranch],
                 tracking_branches: List[TrackingBranch]):

        local_branches = [b for b in local_branches if not b.is_tracking_branch]
        remote_branches = [b for b in remote_branches if not b.is_tracking_branch]
        self.local_branches: Tuple[LocalBranch, ...] = tuple(local_branches)
        self.remote_branches: Tuple[RemoteBranch, ...] = tuple(remote_branches)
        self.tracking_branches: Tuple[TrackingBranch, ...] = tuple(tracking_branches)


def get_remotes(path: Path) -> List[Remote]:
    remotes = offline.get_remotes_info(path)
    remotes = [Remote(path, name) for name in remotes.keys()]

    def sort_by(remote: Remote):
        return remote.name

    return sorted(remotes, key=lambda remote: sort_by(remote))


def get_remote(path: Path, name: str) -> Optional[Remote]:
    remotes = get_remotes(path)
    remote = [r for r in remotes if r.name == name]
    return remote[0] if remote else None


def get_local_branches(path: Path) -> List[LocalBranch]:
    branches = offline.get_local_branches_info(path)
    branches = [LocalBranch(path, branch) for branch in branches]

    def sort_by(branch: LocalBranch):
        return branch.name

    return sorted(branches, key=lambda branch: sort_by(branch))


def get_local_tags(path: Path) -> List[LocalTag]:
    tags = offline.get_local_tags_info(path)
    tags = [LocalTag(path, tag) for tag in tags]

    def sort_by(tag: LocalTag):
        return tag.name

    return sorted(tags, key=lambda tag: sort_by(tag))


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
        submodules.append(Submodule(path, submodule_path,
                                    url=url, commit=submodule_commit,
                                    branch=branch, active=active))

    def sort_by(submodule: Submodule):
        return submodule.submodule_path

    return sorted(submodules, key=lambda submodule: sort_by(submodule))


def get_tracking_branches(path: Path) -> List[TrackingBranch]:
    branches = offline.get_tracking_branches_info(path)
    tracking_branches = []
    for local_branch, info in branches.items():
        tracking_branch = TrackingBranch(path, local_branch,
                                         upstream_branch=info['upstream_branch'],
                                         upstream_remote=info['upstream_remote'],
                                         push_branch=info['push_branch'],
                                         push_remote=info['push_remote'])
        tracking_branches.append(tracking_branch)

    def sort_by(branch: TrackingBranch):
        return f'{branch.name}/{branch.upstream_branch.remote.name}/{branch.upstream_branch.name}'

    return sorted(tracking_branches, key=lambda branch: sort_by(branch))


def get_all_branches(path: Path) -> AllBranches:
    local_branches = get_local_branches(path)
    remote_branches = get_all_remote_branches(path)
    tracking_branches = get_tracking_branches(path)
    return AllBranches(
        local_branches=local_branches,
        remote_branches=remote_branches,
        tracking_branches=tracking_branches
    )


def get_all_remote_branches(path: Path) -> List[RemoteBranch]:
    branches = []
    for remote in get_remotes(path):
        branches += remote.branches

    def sort_by(branch: RemoteBranch):
        return f'{branch.remote.name}/{branch.name}'

    return sorted(branches, key=lambda branch: sort_by(branch))


def get_remote_branches(path: Path, remote: str) -> List[RemoteBranch]:
    branches, default_branch = offline.get_remote_branches_info(path, remote)
    branches = [RemoteBranch(path, branch, remote) for branch in branches]
    if default_branch is not None:
        branches.append(RemoteBranch(path, default_branch, remote, is_default=True))

    def sort_by(branch: RemoteBranch):
        return f'{branch.remote.name}/{branch.name}'

    return sorted(branches, key=lambda branch: sort_by(branch))


def get_remote_tags(path: Path, remote: str) -> List[RemoteTag]:
    tags = online.get_remote_tags_info(path, remote)
    tags = [RemoteTag(path, tag, remote) for tag in tags]

    def sort_by(tag: RemoteTag):
        return f'{tag.remote.name}/{tag.name}'

    return sorted(tags, key=lambda tag: sort_by(tag))


def has_local_branch(path: Path, name: str) -> bool:
    branches = get_local_branches(path)
    return any([branch.name == name for branch in branches])


def has_remote_branch(path: Path, name: str, remote: str) -> bool:
    branches = get_remote_branches(path, remote)
    return any([branch.name == name for branch in branches])


def has_tracking_branch(path: Path, name: str) -> bool:
    branches = get_tracking_branches(path)
    return any([branch.name == name for branch in branches])


def has_local_tag(path: Path, name: str) -> bool:
    tags = get_local_tags(path)
    return any([tag.name == name for tag in tags])


def has_remote_tag(path: Path, name: str, remote: str) -> bool:
    tags = get_remote_tags(path, remote)
    return any([tag.name == name for tag in tags])
