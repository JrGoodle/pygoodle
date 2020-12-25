"""Misc git utils"""

from pathlib import Path
from subprocess import CompletedProcess
from typing import Dict, List, Optional

import pygoodle.command as cmd
import pygoodle.filesystem as fs
from pygoodle.format import Format

from .constants import HEAD, ORIGIN
from .process_output import ProcessOutput


class GitOnline:

    @classmethod
    def pull(cls, path: Path, remote: Optional[str] = None, branch: Optional[str] = None,
             rebase: bool = False) -> CompletedProcess:
        """Pull upstream changes"""

        remote = '' if remote is None else remote
        # FIXME: Make sure branch args are correct for local and remote
        branch = '' if branch is None else f'refs/heads/{branch}:refs/remotes/{remote}/heads/{branch}'
        args = ''
        if rebase:
            args += ' --rebase '
        return cmd.run(f'git pull {args} {remote} {branch}', cwd=path)

    @classmethod
    def pull_lfs(cls, path: Path) -> CompletedProcess:
        """Pull lfs files"""

        return cmd.run('git lfs pull', cwd=path)

    # See: https://github.blog/2020-12-21-get-up-to-speed-with-partial-clone-and-shallow-clone/
    @classmethod
    def clone(cls, path: Path, url: str, depth: Optional[int] = None, branch: Optional[str] = None,
              jobs: Optional[int] = None, single_branch: bool = False, blobless: bool = False,
              treeless: bool = False) -> CompletedProcess:
        if path.is_dir():
            if fs.has_contents(path):
                raise Exception(f'Existing directory at clone path {path}')
            fs.remove_dir(path)

        args = ''
        if branch is not None:
            args += f' --branch {branch} '
        if single_branch:
            args += ' --single-branch '
        if jobs is not None:
            args += f' --jobs {jobs} '
        if depth is not None:
            args += f' --depth {depth} '

        assert not (blobless and treeless)
        if blobless:
            args += ' --filter=blob:none '
        elif treeless:
            args += ' --filter=tree:0 '

        return cmd.run(f'git clone {args} {url} {path}')

    @classmethod
    def push(cls, path: Path, local_branch: Optional[str] = None, remote_branch: Optional[str] = None,
             remote: Optional[str] = None, force: bool = False) -> CompletedProcess:
        args = ''
        if force:
            args += ' --force '
        if local_branch is None:
            return cmd.run('git push', cwd=path)
        else:
            remote_branch = local_branch if remote_branch is None else remote_branch
            remote = '' if remote is None else remote
            return cmd.run(f'git push {args} {remote} refs/heads/{local_branch}:refs/heads/{remote_branch}', cwd=path)

    @classmethod
    def fetch(cls, path: Path, prune: bool = False, tags: bool = False, depth: Optional[int] = None,
              remote: Optional[str] = None, ref: Optional[str] = None, unshallow: bool = False) -> CompletedProcess:
        args = ''
        if prune:
            args += ' --prune '
        if tags:
            args += ' --tags '
        if depth is not None:
            args += f' --depth {depth}'
        if unshallow:
            args += ' --unshallow '
        remote = '' if remote is None else remote
        ref = '' if ref is None else ref
        return cmd.run(f"git fetch {args} {remote} {ref}", cwd=path)

    @classmethod
    def delete_remote_tag(cls, path: Path, name: str, remote: str = ORIGIN) -> CompletedProcess:
        return cmd.run(f'git push {remote} :refs/tags/{name}', cwd=path)

    @classmethod
    def delete_remote_branch(cls, path: Path, branch: str, remote: str = ORIGIN) -> CompletedProcess:
        # return cmd.run(f"git push {remote} --force --delete {branch}", cwd=path)
        return cmd.run(f"git push {remote} --force :refs/heads/{branch}", cwd=path)

    @classmethod
    def create_upstream_branch(cls, path: Path, branch: str, upstream_branch: str,
                               remote: str = ORIGIN) -> CompletedProcess:
        return cmd.run(f"git push -u {remote} refs/heads/{branch}:refs/heads/{upstream_branch}", cwd=path)

    @classmethod
    def branch_exists_at_remote_url(cls, url: str, branch: str) -> bool:
        output = cmd.get_stdout(f'git ls-remote --heads {url} {branch}')
        if output is None:
            # TODO: Should this return None?
            return False
        return bool(output)

    @classmethod
    def branch_exists_on_remote(cls, path: Path, branch: str, remote: str = ORIGIN) -> bool:
        output = cmd.get_stdout(f'git ls-remote --heads {remote} {branch}', cwd=path)
        if output is None:
            # TODO: Should this return None?
            return False
        return bool(output)

    @classmethod
    def get_default_branch(cls, url: str) -> Optional[str]:
        """Get default branch from remote repo"""

        command = f'git ls-remote --symref {url} {HEAD}'
        output = cmd.get_stdout(command)
        if output is None:
            return None
        output_list = output.split()
        branch = [Format.remove_prefix(chunk, 'refs/heads/')
                  for chunk in output_list if chunk.startswith('refs/heads/')]
        return branch[0]

    @classmethod
    def submodule_update(cls, path: Path, init: bool = False, depth: Optional[int] = None, single_branch: bool = False,
                         jobs: Optional[int] = None, recursive: bool = False, remote: bool = False,
                         no_fetch: bool = False, checkout: bool = False, rebase: bool = False, merge: bool = False,
                         paths: Optional[List[Path]] = None) -> CompletedProcess:
        args = ''
        if init:
            args += ' --init '
        if single_branch:
            args += ' --single-branch '
        if jobs is not None:
            args += f' --jobs {jobs} '
        if depth is not None:
            args += f' --depth {depth} '
        if recursive is not None:
            args += ' --recursive '
        if remote:
            args += ' --remote '
        if no_fetch:
            args += ' --no-fetch '

        # TODO: Validate that at most one of these is True
        if checkout:
            args += ' --checkout '
        if merge:
            args += ' --merge '
        if rebase:
            args += ' --rebase '

        if paths is not None and paths:
            paths = ' '.join([str(p) for p in paths])
        else:
            paths = ''
        return cmd.run(f'git submodule update {args} {paths}', cwd=path)

    @classmethod
    def get_remote_tag_sha(cls, path: Path, name: str, remote: str = ORIGIN) -> Optional[str]:
        tags = GitOnline.get_remote_tags_info(path, remote=remote)
        tag = [t for t in tags if t == name]
        return tag[1] if tag else None

    @classmethod
    def get_remote_tags_info(cls, path: Path, remote: str = ORIGIN) -> Dict[str, str]:
        output = cmd.get_stdout(f"git ls-remote --tags {remote}", cwd=path)
        if output is None:
            return {}
        return ProcessOutput.tag_shas(output)

    @classmethod
    def get_remote_tag(cls, path: Path, name: str, remote: str = ORIGIN) -> Optional[str]:
        tags = GitOnline.get_remote_tags_info(path, remote=remote)
        tag = [t for t in tags if t == name]
        return tag[0] if tag else None

    @classmethod
    def get_remote_branches_info(cls, path: Path, remote: str = ORIGIN) -> Dict[str, str]:
        output = cmd.get_stdout(f'git ls-remote --heads {remote}', cwd=path)
        return ProcessOutput.branch_shas(output)
