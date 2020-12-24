"""git model factory

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from pathlib import Path
from typing import List, Optional, Tuple

from pygoodle.git.offline import GitOffline
from pygoodle.git.online import GitOnline

from .branch.local_branch import LocalBranch
from .branch.remote_branch import RemoteBranch
from .branch.tracking_branch import TrackingBranch
from .remote import Remote
from .submodule import Submodule
from .tag.local_tag import LocalTag
from .tag.remote_tag import RemoteTag


class AllBranches:

    def __init__(self, local_branches: List[LocalBranch], remote_branches: List[RemoteBranch],
                 tracking_branches: List[TrackingBranch]):

        local_branches = [b for b in local_branches if not b.is_tracking_branch]
        remote_branches = [b for b in remote_branches if not b.is_tracking_branch]
        self.local_branches: Tuple[LocalBranch, ...] = tuple(local_branches)
        self.remote_branches: Tuple[RemoteBranch, ...] = tuple(remote_branches)
        self.tracking_branches: Tuple[TrackingBranch, ...] = tuple(tracking_branches)


class GitFactory:

    @classmethod
    def get_remotes(cls, path: Path) -> List[Remote]:
        remotes = GitOffline.get_remotes_info(path)
        remotes = [Remote(path, name) for name in remotes.keys()]

        def sort_by(remote: Remote):
            return remote.name

        return sorted(remotes, key=lambda remote: sort_by(remote))

    @classmethod
    def get_remote(cls, path: Path, name: str) -> Optional[Remote]:
        remotes = GitFactory.get_remotes(path)
        remote = [r for r in remotes if r.name == name]
        return remote[0] if remote else None

    @classmethod
    def has_remote_with_name(cls, path: Path, name: str) -> bool:
        remotes = GitFactory.get_remotes(path)
        remote = [r for r in remotes if r.name == name]
        return bool(remote)

    @classmethod
    def has_remote_with_fetch_url(cls, path: Path, url: str) -> bool:
        remotes = GitFactory.get_remotes(path)
        remote = [r for r in remotes if r.fetch_url is not None and r.fetch_url == url]
        return bool(remote)

    @classmethod
    def has_remote_with_push_url(cls, path: Path, url: str) -> bool:
        remotes = GitFactory.get_remotes(path)
        remote = [r for r in remotes if r.push_url is not None and r.push_url == url]
        return bool(remote)

    @classmethod
    def get_local_branches(cls, path: Path) -> List[LocalBranch]:
        branches = GitOffline.get_local_branches_info(path)
        branches = [LocalBranch(path, branch) for branch in branches]

        def sort_by(branch: LocalBranch):
            return branch.name

        return sorted(branches, key=lambda branch: sort_by(branch))

    @classmethod
    def get_local_tags(cls, path: Path) -> List[LocalTag]:
        tags = GitOffline.get_local_tags_info(path)
        tags = [LocalTag(path, tag) for tag in tags]

        def sort_by(tag: LocalTag):
            return tag.name

        return sorted(tags, key=lambda tag: sort_by(tag))

    @classmethod
    def get_submodules(cls, path: Path) -> List[Submodule]:
        submodules_info = GitOffline.get_submodules_info(path)
        submodules = []
        for key in submodules_info.keys():
            submodule_info = submodules_info[key]
            url = submodule_info['url']
            submodule_path = Path(submodule_info['path'])
            branch = submodule_info['branch'] if 'branch' in submodule_info else None
            active = submodule_info['active'] if 'active' in submodule_info else None
            active = True if active == 'true' else False
            submodule_commit = GitOffline.get_submodule_commit(path, submodule_path)
            submodules.append(Submodule(path, submodule_path,
                                        url=url, commit=submodule_commit,
                                        branch=branch, active=active))

        def sort_by(submodule: Submodule):
            return submodule.submodule_path

        return sorted(submodules, key=lambda submodule: sort_by(submodule))

    @classmethod
    def get_tracking_branches(cls, path: Path) -> List[TrackingBranch]:
        branches = GitOffline.get_tracking_branches_info(path)
        tracking_branches = []
        for local_branch, info in branches.items():
            tracking_branch = TrackingBranch(path,
                                             local_branch=local_branch,
                                             upstream_branch=info['upstream_branch'],
                                             upstream_remote=info['upstream_remote'],
                                             push_branch=info['push_branch'],
                                             push_remote=info['push_remote'])
            tracking_branches.append(tracking_branch)

        def sort_by(branch: TrackingBranch):
            return f'{branch.name}/{branch.upstream_branch.remote.name}/{branch.upstream_branch.name}'

        return sorted(tracking_branches, key=lambda branch: sort_by(branch))

    @classmethod
    def get_all_branches(cls, path: Path) -> AllBranches:
        local_branches = GitFactory.get_local_branches(path)
        remote_branches = GitFactory.get_all_remote_branches(path)
        tracking_branches = GitFactory.get_tracking_branches(path)
        return AllBranches(
            local_branches=local_branches,
            remote_branches=remote_branches,
            tracking_branches=tracking_branches
        )

    @classmethod
    def get_all_remote_branches(cls, path: Path) -> List[RemoteBranch]:
        branches = []
        for remote in GitFactory.get_remotes(path):
            branches += remote.branches

        def sort_by(branch: RemoteBranch):
            return f'{branch.remote.name}/{branch.name}'

        return sorted(branches, key=lambda branch: sort_by(branch))

    @classmethod
    def get_remote_branches(cls, path: Path, remote: str) -> List[RemoteBranch]:
        branches, default_branch = GitOffline.get_remote_branches_info(path, remote)
        branches = [RemoteBranch(path, branch, remote) for branch in branches]
        if default_branch is not None:
            branches.append(RemoteBranch(path, default_branch, remote, is_default=True))

        def sort_by(branch: RemoteBranch):
            return f'{branch.remote.name}/{branch.name}'

        return sorted(branches, key=lambda branch: sort_by(branch))

    @classmethod
    def get_remote_tags(cls, path: Path, remote: str) -> List[RemoteTag]:
        tags = GitOnline.get_remote_tags_info(path, remote)
        tags = [RemoteTag(path, tag, remote) for tag in tags]

        def sort_by(tag: RemoteTag):
            return f'{tag.remote.name}/{tag.name}'

        return sorted(tags, key=lambda tag: sort_by(tag))

    @classmethod
    def has_local_branch(cls, path: Path, name: str) -> bool:
        branches = GitFactory.get_local_branches(path)
        return any([branch.name == name for branch in branches])

    @classmethod
    def has_remote_branch(cls, path: Path, name: str, remote: str) -> bool:
        branches = GitFactory.get_remote_branches(path, remote)
        return any([branch.name == name for branch in branches])

    @classmethod
    def has_tracking_branch(cls, path: Path, name: str) -> bool:
        branches = GitFactory.get_tracking_branches(path)
        return any([branch.name == name for branch in branches])

    @classmethod
    def has_local_tag(cls, path: Path, name: str) -> bool:
        tags = GitFactory.get_local_tags(path)
        return any([tag.name == name for tag in tags])

    @classmethod
    def has_remote_tag(cls, path: Path, name: str, remote: str) -> bool:
        tags = GitFactory.get_remote_tags(path, remote)
        return any([tag.name == name for tag in tags])
