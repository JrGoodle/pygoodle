"""Misc git utils"""

from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Dict, List, Optional

import pygoodle.command as cmd
import pygoodle.filesystem as fs
import pygoodle.git.process_output as process
from pygoodle.format import Format
from pygoodle.git.model import Branch, LocalBranch, Ref, Remote, RemoteBranch, Submodule, TrackingBranch
from pygoodle.git.constants import *


def get_remotes(path: Path) -> List[Remote]:
    output = cmd.get_stdout('git remote -v', cwd=path)
    remotes = process.remotes(output)
    return [Remote(path, name, fetch_url=values[FETCH_URL], push_url=values[PUSH_URL])
            for name, values in remotes.items()]


def existing_remote(path: Path, name: str) -> bool:
    remotes = get_remotes(path)
    return any([name == r.name for r in remotes])


def get_remote(path: Path, name: str) -> Optional[Remote]:
    remotes = get_remotes(path)
    remote = [r for r in remotes if r.name == name]
    return remote[0] if remote else None


def get_remote_url(path: Path, remote_name: str) -> str:
    """Get url of remote

    :param Path path: Path to git repo
    :param str remote_name: Remote name
    :return: URL of remote
    """

    return cmd.get_stdout(f'git remote get-url {remote_name}', cwd=path)


def create_remote(path: Path, name: str, url: str, fetch: bool = False, tags: bool = False) -> None:
    args = ''
    if fetch:
        args += ' -f '
    if tags:
        args += ' --tags '
    cmd.get_stdout(f'git remote add {name} {url}', cwd=path)


def find_rev_by_timestamp(path: Path, timestamp: str, ref: str, author: Optional[str] = None) -> str:
    """Find rev by timestamp

    :param Path path: Path to git repo
    :param str timestamp: Commit ref timestamp
    :param str ref: Reference ref
    :param Optional[str] author: Commit author
    :return: Commit sha at or before timestamp
    """

    args = ''
    if author is not None:
        args += f' --author {author} '
    return cmd.get_stdout(f'git log -1 --format=%H --before={timestamp} {ref}', cwd=path)


def install_lfs_hooks(path: Path) -> CompletedProcess:
    """Install git lfs hooks"""

    return cmd.run('git lfs install --local', cwd=path)


def rename_remote(path: Path, old_name: str, new_name: str) -> CompletedProcess:
    return cmd.run(f'git remote rename {old_name} {new_name}', cwd=path)


def get_default_branch(path: Path, remote: str) -> Optional[str]:
    """Get default branch from local repo"""

    try:
        command = f'git symbolic-ref refs/remotes/{remote}/{HEAD}'
        output = cmd.get_stdout(command, cwd=path)
        output_list = output.split()
        branch = [Format.remove_prefix(chunk, f'refs/remotes/{remote}/') for chunk in output_list
                  if chunk.startswith(f'refs/remotes/{remote}/')]
        return branch[0]
    except CalledProcessError:
        return None


def save_default_branch(path: Path, remote: str, branch: str) -> None:
    """Save default branch"""

    git_dir = path / '.git'
    if not git_dir.exists():
        return
    remote_head_ref = git_dir / 'refs' / 'remotes' / remote / HEAD
    if not remote_head_ref.exists():
        fs.make_dir(remote_head_ref.parent, exist_ok=True)
        contents = f'ref: refs/remotes/{remote}/{branch}'
        remote_head_ref.touch()
        remote_head_ref.write_text(contents)


def current_timestamp(path: Path) -> str:
    """Current timestamp of HEAD commit"""

    return cmd.get_stdout('git log -1 --format=%cI', cwd=path)


def is_repo_cloned(path: Path) -> bool:
    """Check if a git repository exists

    :param Path path: Repo path
    :return: True, if .git directory exists inside path
    """

    return path.is_dir() and has_git_directory(path) and fs.has_contents(path)


def is_dirty(path: Path) -> bool:
    result = cmd.run_silent(f'git diff-index --quiet {HEAD} --', cwd=path)
    return result.returncode == 0


def is_rebase_in_progress(path: Path) -> bool:
    rebase_merge = path / ".git" / "rebase-merge"
    rebase_apply = path / ".git" / "rebase-apply"
    rebase_merge_exists = rebase_merge.exists() and rebase_merge.is_dir()
    rebase_apply_exists = rebase_apply.exists() and rebase_apply.is_dir()
    return rebase_merge_exists or rebase_apply_exists


def has_local_branch(path: Path, branch: str) -> bool:
    branches = get_local_branches(path)
    return branch in branches


def has_local_tag(path: Path, tag: str) -> bool:
    tags = get_local_tags(path)
    return tag in tags


def get_local_branches(path: Path) -> List[LocalBranch]:
    output = cmd.get_stdout("git branch", cwd=path)
    lines = output.splitlines()

    def process_line(line: str) -> str:
        return line if line.startswith('*') else line.split()[1]

    return [LocalBranch(path, process_line(line)) for line in lines]


def get_local_tags(path: Path) -> List[str]:
    info = get_local_tags_info(path)
    return list(info.keys())


def get_local_tags_info(path: Path) -> Dict[str, str]:
    output = cmd.get_stdout("git show-ref --tags", cwd=path)
    return process.tag_shas(output)


def get_untracked_files(path: Path) -> List[str]:
    output = cmd.get_stdout('git ls-files . --exclude-standard --others', cwd=path)
    return output.split()


def new_commits_count(path: Path, upstream: bool = False, remote: str = ORIGIN) -> int:
    """Returns the number of new commits

    :param Path path: Path to git repo
    :param bool upstream: Whether to find number of new upstream or local commits
    :param str remote: Git remote name
    :return: Int number of new commits
    """

    local_branch = current_branch(path)
    upstream_branch = get_upstream_branch(path, local_branch)
    if local_branch is None or upstream_branch is None:
        return 0

    try:
        local_sha = get_branch_commit_sha(path, local_branch)
        remote_sha = get_branch_commit_sha(path, upstream_branch.name, remote=remote)
        commits = f'{local_sha}...{remote_sha}'
        output = cmd.get_stdout(f'git rev-list --count --left-right {commits}', cwd=path)
        index = 1 if upstream else 0
        return int(output.split()[index])
    except (CalledProcessError, ValueError):
        return 0


def has_untracked_files(path: Path) -> bool:
    files = get_untracked_files(path)
    return bool(files)


def has_git_directory(path: Path) -> bool:
    return Path(path / ".git").is_dir()


def is_submodule_placeholder(path: Path) -> bool:
    return path.is_dir() and fs.is_empty_dir(path)


def has_submodules(path: Path) -> bool:
    submodules = get_submodules(path)
    return bool(submodules)


def get_submodules(path: Path, initialized: bool = False) -> List[Submodule]:
    submodule_info = get_submodule_info(path, initialized=initialized)
    submodules = []
    for key in submodule_info.keys():
        url = submodule_info[key]['url']
        submodule_path = Path(submodule_info[key]['path'])
        branch = submodule_info[key]['branch'] if 'branch' in submodule_info[key] else None
        active = submodule_info[key]['active'] if 'active' in submodule_info[key] else None
        active = True if active == 'true' else False
        submodule_commit = get_submodule_commit(path, submodule_path)
        submodule = Submodule(path, submodule_path, url=url, commit=submodule_commit, branch=branch, active=active)
        submodules.append(submodule)
    return submodules


def get_submodule_commit(path: Path, submodule_path: Path) -> str:
    output = cmd.get_stdout(f'git ls-tree master {submodule_path}', cwd=path)
    return output.split()[2]


def get_submodule_info(path: Path, initialized: bool) -> Dict[str, Dict[str, str]]:
    file = '.git/config' if initialized else '.gitmodules'
    output = get_config_info(path, 'submodule', file)
    submodules = process.submodules(output)
    return submodules


def get_config_info(path: Path, name: str, file: str) -> List[str]:
    output = cmd.get_stdout(f'git config --file {file} --get-regexp {name}', cwd=path)
    return output.split()


def get_submodule_git_dir(path: Path) -> Optional[Path]:
    git_file = path / '.git'
    if not git_file.is_file():
        return None
    git_contents = git_file.read_text()
    git_path = Path(git_contents.split()[1])
    git_path = git_file.parent / git_path
    return git_path.resolve(strict=False)


def is_submodule_initialized(path: Path, submodule_path: Path) -> bool:
    if not repo_has_submodule(path, submodule_path):
        return False
    submodules = get_submodules(path, initialized=True)
    return bool(submodules)


def is_submodule_cloned(path: Path, submodule_path: Path) -> bool:
    if not is_submodule_initialized(path, submodule_path):
        return False
    git_dir = get_submodule_git_dir(path)
    return git_dir.is_dir() and fs.has_contents(git_dir)


def repo_has_submodule(path: Path, submodule_path: Path) -> bool:
    submodules = get_submodules(path)
    return any([s.submodule_path == submodule_path for s in submodules])


def lfs_hooks_installed(path: Path) -> bool:
    hooks = [
        ['git lfs pre-push', '.git/hooks/pre-push'],
        ['git lfs post-checkout', '.git/hooks/post-checkout'],
        ['git lfs post-commit', '.git/hooks/post-commit'],
        ['git lfs post-merge', '.git/hooks/post-merge']
    ]

    for hook in hooks:
        result = cmd.run_silent(f"grep -m 1 '{hook[0]}' '{hook[1]}", cwd=path)
        if result.returncode != 0:
            return False
    return True


def lfs_filters_installed(path: Path) -> bool:
    lfs_filters = [
        'smudge',
        'clean',
        'process',
        'required'
    ]

    for lfs_filter in lfs_filters:
        result = cmd.run_silent(f'git config --get filter.lfs.{lfs_filter}', cwd=path)
        if result.returncode != 0:
            return False
    return True


def uninstall_lfs_hooks_filters(path: Path) -> List[CompletedProcess]:
    commands = [
        'git lfs uninstall --local',
        'git lfs uninstall --system',
        'git lfs uninstall'
    ]

    results = []
    for command in commands:
        result = cmd.run_silent(command)
        results.append(result)
    # result = cmd.run("git config --system --unset filter.lfs.clean", cwd=path)
    # result = cmd.run("git config --system --unset filter.lfs.smudge", cwd=path)
    # result = cmd.run("git config --system --unset filter.lfs.process", cwd=path)
    # result = cmd.run("git config --system --unset filter.lfs.required", cwd=path)
    assert not lfs_hooks_installed(path)
    assert not lfs_filters_installed(path)
    return results


def is_lfs_file_pointer(path: Path, file: str) -> bool:
    output = cmd.get_stdout(f'git lfs ls-files -I "{file}"', cwd=path)
    components = output.split()
    return components[1] == '-'


def is_lfs_file_not_pointer(path: Path, file: str) -> bool:
    output = cmd.get_stdout(f'git lfs ls-files -I "{file}"', cwd=path)
    components = output.split()
    return components[1] == '*'


def get_git_config(path: Path) -> str:
    return cmd.get_stdout('git config --list --show-origin', cwd=path)


def stash(path: Path) -> CompletedProcess:
    return cmd.run('git stash', cwd=path)


def status(path: Path, verbose: bool = False) -> CompletedProcess:
    args = ''
    if verbose:
        args = '-vv'
    return cmd.run(f'git status {args}', cwd=path)


def current_head_commit_sha(path: Path, short: bool = False) -> str:
    args = ''
    if short:
        args = '--short'
    return cmd.get_stdout(f'git rev-parse {args} {HEAD}', cwd=path)


def get_branch_commit_sha(path: Path, branch: str, remote: Optional[str] = None) -> str:
    if remote is not None:
        return cmd.get_stdout(f"git rev-parse {remote}/{branch}", cwd=path)
    else:
        return cmd.get_stdout(f"git rev-parse {branch}", cwd=path)


def add(path: Path, files: List[str]) -> CompletedProcess:
    files = " ".join(files)
    return cmd.run(f"git add {files}", cwd=path)


def commit(path: Path, message: str) -> CompletedProcess:
    return cmd.run(f"git commit -m '{message}'", cwd=path)


def create_local_branch(path: Path, branch: str) -> CompletedProcess:
    return cmd.run(f"git branch {branch} {HEAD}", cwd=path)


def delete_local_branch(path: Path, branch: str) -> CompletedProcess:
    return cmd.run(f"git branch -d {branch}", cwd=path)


def delete_local_tag(path: Path, name: str) -> CompletedProcess:
    return cmd.run(f'git tag --delete {name}', cwd=path)


def check_ref_format(refname: str) -> bool:
    """Check git ref format

    :param str refname: Files to git add
    """

    result = cmd.run_silent(f'git check-ref-format --normalize {refname}')
    return result.returncode == 0


def reset_timestamp(path: Path, timestamp: str, ref: Ref, author: Optional[str] = None) -> CompletedProcess:
    """Reset branch to upstream or checkout tag/sha as detached HEAD

    :param Path path: Path to git repo
    :param str timestamp: Commit ref timestamp
    :param Optional[str] author: Commit author
    :param Ref ref: Reference ref
    :raise ClowderGitError:
    """

    rev = find_rev_by_timestamp(path, timestamp, ref.short_ref, author=author)
    return checkout(path, rev)


def clean_submodules(path: Path, recursive: bool = False) -> CompletedProcess:
    return foreach_submodule(path, 'git clean -ffdx', recursive=recursive)


def reset_submodules(path: Path, recursive: bool = False) -> CompletedProcess:
    return foreach_submodule(path, 'git reset --hard', recursive=recursive)


def foreach_submodule(path: Path, command: str, recursive: bool = False) -> CompletedProcess:
    args = ''
    if recursive:
        args += ' --recursive '
    return cmd.run(f'git submodule foreach {args} {command}', cwd=path)


def clean(path: Path, untracked_directories: bool = False, force: bool = False,
          ignored: bool = False, untracked_files: bool = False) -> CompletedProcess:
    args = '-'
    if untracked_directories:
        args += 'd'
    if force:
        args += 'f'
    if ignored:
        args += 'X'
    if untracked_files:
        args += 'x'
    args = '' if args == '-' else args
    return cmd.run(f"git clean {args}", cwd=path)


def checkout(path: Path, ref: str) -> CompletedProcess:
    return cmd.run(f"git checkout {ref}", cwd=path)


def local_branch_exists(path: Path, branch: str) -> bool:
    result = cmd.run_silent(f"git rev-parse --quiet --verify refs/heads/{branch}", cwd=path)
    return result.returncode == 0


def get_tracking_branches(path: Path) -> List[TrackingBranch]:
    local_branches = get_local_branches(path)

    upstream_branches = []
    for branch in local_branches:
        upstream_branch = get_upstream_branch(path, branch.name)
        if upstream_branch is not None and isinstance(upstream_branch, RemoteBranch):
            upstream_branches.append(upstream_branch)
    return [TrackingBranch(path, b.name, upstream_branch=b) for b in upstream_branches]


def get_upstream_branch(path: Path, branch: str) -> Optional[Branch]:
    return rev_parse_tracking_branch(path, branch, 'upstream')


def get_push_branch(path: Path, branch: str) -> Optional[Branch]:
    return rev_parse_tracking_branch(path, branch, 'push')


def rev_parse_tracking_branch(path: Path, branch: str, arg: str) -> Optional[Branch]:
    try:
        output = cmd.get_stdout(f'git rev-parse --symbolic-full-name {branch}@{{{arg}}}', cwd=path)
    except CalledProcessError:
        return None
    remote, branch = process.tracking_branches(output)
    if remote is None:
        return LocalBranch(path, branch)
    else:
        remote = get_remote(path, remote)
        return RemoteBranch(path, branch, remote=remote)


def get_full_branch_ref(path: Path, branch: str) -> str:
    return cmd.get_stdout(f'git rev-parse --symbolic-full-name {branch}', cwd=path)


def git_remote_show(path: Path, remote: str) -> str:
    return cmd.get_stdout(f'git remote show {remote}', cwd=path)


def has_tracking_branch(path: Path, branch: str) -> bool:
    result = cmd.run_silent(f'git config --get branch.{branch}.merge', cwd=path)
    return result.returncode == 0


def check_remote_url(path: Path, remote, url) -> bool:
    output = cmd.get_stdout(f"git remote get-url {remote}", cwd=path)
    return output == url


def is_on_branch(path: Path, branch: str) -> bool:
    return current_branch(path) == branch


def current_branch(path: Path) -> str:
    return cmd.get_stdout(f'git rev-parse --abbrev-ref {HEAD}', cwd=path)


def set_upstream_branch(path: Path, branch: str, upstream_branch: str,
                        remote: Optional[str] = None) -> CompletedProcess:
    remote_arg = ''
    if remote is not None:
        remote_arg = f'{remote}/'

    return cmd.run(f'git branch --set-upstream-to={remote_arg}{upstream_branch} {branch}', cwd=path)


def git_config_unset_all_local(path: Path, variable: str) -> CompletedProcess:
    """Unset all local git config values for given variable key

    :param Path path: Path to git repo
    :param str variable: Fully qualified git config variable
    """

    try:
        return cmd.run(f'git config --local --unset-all {variable}', cwd=path)
    except CalledProcessError as err:
        if err.returncode != 5:  # git returns error code 5 when trying to unset variable that doesn't exist
            raise


def git_config_add_local(path: Path, variable: str, value: str) -> CompletedProcess:
    """Add local git config value for given variable key

    :param Path path: Path to git repo
    :param str variable: Fully qualified git config variable
    :param str value: Git config value
    """

    return cmd.run(f'git config --local --add {variable} {value}', cwd=path)


def is_detached(path: Path) -> bool:
    return current_branch(path) == HEAD


def get_tag_commit_sha(path: Path, tag: str) -> str:
    return cmd.get_stdout(f'git rev-list -n 1 {tag}', cwd=path)


def get_sha(path: Path, ref: str = HEAD) -> str:
    return cmd.get_stdout(f'git rev-parse {ref}', cwd=path)


def number_of_commits_between_refs(path: Path, first: str, second: str) -> int:
    output = cmd.get_stdout(f"git rev-list {first}..{second} --count", cwd=path)
    return int(output)


def reset(path: Path, ref: str = HEAD, hard: bool = False) -> CompletedProcess:
    args = ''
    if hard:
        args = '--hard'
    return cmd.run(f"git reset {args} {ref}", cwd=path)


def reset_back_by_number_of_commits(path: Path, number: int) -> CompletedProcess:
    sha = current_head_commit_sha(path)
    result = cmd.run(f"git reset --hard {HEAD}~{number}", cwd=path)
    assert number_of_commits_between_refs(path, HEAD, sha) == number
    return result


def has_no_commits_between_refs(path: Path, start: str, end: str) -> bool:
    result_1 = number_of_commits_between_refs(path, start, end) == 0
    result_2 = number_of_commits_between_refs(path, end, start) == 0
    return result_1 and result_2


def is_ahead_by_number_commits(path: Path, start: str, end: str, number_commits: int) -> bool:
    return number_commits_ahead(path, start, end) == number_commits


def is_behind_by_number_commits(path: Path, start: str, end: str, number_commits: int) -> bool:
    return number_commits_behind(path, start, end) == number_commits


def number_commits_ahead(path: Path, start: str, end: str) -> int:
    return number_of_commits_between_refs(path, end, start)


def number_commits_behind(path: Path, start: str, end: str) -> int:
    return number_of_commits_between_refs(path, start, end)


def abort_rebase(path: Path) -> CompletedProcess:
    return cmd.run('git rebase --abort', cwd=path)


def get_commit_messages_behind(path: Path, ref: str, count: int = 1) -> List[str]:
    results = []
    commit_number = 0
    while commit_number < count:
        result = get_commit_message(path, f"{ref}~{commit_number}")
        results.append(result)
        commit_number += 1
    return results


def get_commit_message(path: Path, ref: str) -> str:
    return cmd.get_stdout(f"git log --format=%B -n 1 {ref}", cwd=path)


def is_shallow_repo(path: Path) -> bool:
    output = cmd.get_stdout("git rev-parse --is-shallow-repository", cwd=path)
    return output == "true"


def has_remote_branch(path: Path, branch: str, remote: Remote) -> bool:
    branches = get_remote_branches(path, remote=remote)
    return branch in [b.name for b in branches]


def get_remote_branches(path: Path, remote: Remote) -> List[RemoteBranch]:
    output = cmd.get_stdout(f'git branch -r {remote}', cwd=path)
    _, branches = process.remote_branches(output, remote=remote.name)
    branches = [RemoteBranch(path, b, remote) for b in branches]
    return branches
