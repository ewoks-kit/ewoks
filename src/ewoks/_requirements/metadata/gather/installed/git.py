import subprocess
from pathlib import Path
from typing import List
from typing import Optional

from ....models.distro import GitInfo


def git_info_from_path(path: Path) -> Optional[GitInfo]:
    """
    Return GitInfo for a local path, or None if not a git repository.
    """
    try:
        commit = _git(["rev-parse", "HEAD"], path)
    except Exception:
        return None

    try:
        uncomitted_changes = bool(_git(["status", "--porcelain"], path))
    except Exception:
        uncomitted_changes = False

    remote_name = _find_remote_for_commit(path, commit)
    if remote_name:
        try:
            remote_url = _git(["remote", "get-url", remote_name], path)
        except Exception:
            remote_url = None
    else:
        remote_url = None

    return GitInfo(
        commit=commit, remote=remote_url, uncomitted_changes=uncomitted_changes
    )


def _find_remote_for_commit(path: Path, commit: str) -> Optional[str]:
    """
    Return the name of a remote that contains the given commit.
    """
    try:
        remotes = _git_lines(["remote"], path)
    except Exception:
        return None

    if not remotes:
        return None

    if "origin" in remotes:
        remotes = ["origin"] + [r for r in remotes if r != "origin"]

    try:
        branches = _git_lines(["branch", "-r", "--contains", commit], path)
    except Exception:
        return None

    for remote in remotes:
        prefix = f"{remote}/"
        if any(b.startswith(prefix) for b in branches):
            return remote

    return None


def _git(cmd: List[str], repo: Path) -> str:
    return subprocess.check_output(
        ["git"] + cmd, cwd=repo, stderr=subprocess.DEVNULL, text=True
    ).strip()


def _git_lines(cmd: List[str], repo: Path) -> List[str]:
    out = _git(cmd, repo)
    return [line.strip() for line in out.splitlines() if line.strip()]
