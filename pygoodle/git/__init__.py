"""pygoodle git module __init__

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Dict

from .model import (
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

from .constants import (
    HEAD,
    ORIGIN,
    FETCH_URL,
    PUSH_URL,
    GITMODULES,
    GIT_CONFIG
)

GitConfig = Dict[str, str]
