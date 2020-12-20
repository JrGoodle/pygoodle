"""pygoodle git module __init__

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Dict

from pygoodle.git.constants import (
    HEAD,
    ORIGIN,
    FETCH_URL,
    PUSH_URL,
    GITMODULES,
    GIT_CONFIG
)

from pygoodle.git.model import (
    AllBranches,
    Branch,
    Commit,
    LocalBranch,
    LocalTag,
    Protocol,
    Ref,
    Remote,
    RemoteBranch,
    RemoteTag,
    Repo,
    Submodule,
    Tag,
    TrackingBranch
)

GitConfig = Dict[str, str]
