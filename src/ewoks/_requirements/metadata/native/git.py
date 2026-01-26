import subprocess
from pathlib import Path
from typing import Optional

from .types import GitInfo


def git_info_from_path(path: Path) -> Optional[GitInfo]:
    """
    Return GitInfo for a local path, or None if not a git repository.
    """
    try:
        commit = _git(["rev-parse", "HEAD"], path)
    except Exception:
        return None

    try:
        dirty = bool(_git(["status", "--porcelain"], path))
    except Exception:
        dirty = False

    remote_name = _find_remote_for_commit(path, commit)
    if remote_name:
        try:
            remote_url = _git(["remote", "get-url", remote_name], path)
        except Exception:
            remote_url = None
    else:
        remote_url = None

    return GitInfo(commit=commit, remote=remote_url, dirty=dirty)


def normalize_git_url(url: str, preserve_ssh: bool = False) -> str:
    """
    Return a PEP 508-compatible VCS URL, prefixed with 'git+'.
    """
    # SCP-like SSH syntax: git@host:group/repo.git
    if url.startswith("git@"):
        host, path = url[len("git@") :].split(":", 1)
        if preserve_ssh:
            return f"git+ssh://git@{host}/{path}"
        return f"git+https://{host}/{path}"

    # Explicit SSH URL
    if url.startswith("ssh://"):
        if preserve_ssh:
            return f"git+{url}"

        # ssh://git@host/group/repo.git -> https://host/group/repo.git
        without_scheme = url[len("ssh://") :]
        if without_scheme.startswith("git@"):
            without_scheme = without_scheme[len("git@") :]
        return f"git+https://{without_scheme}"

    # HTTP(S)
    if url.startswith("http://") or url.startswith("https://"):
        return f"git+{url}"

    # Unknown / already normalized
    return url


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


def _git(cmd: list[str], repo: Path) -> str:
    return subprocess.check_output(
        ["git"] + cmd, cwd=repo, stderr=subprocess.DEVNULL, text=True
    ).strip()


def _git_lines(cmd: list[str], repo: Path) -> list[str]:
    out = _git(cmd, repo)
    return [line.strip() for line in out.splitlines() if line.strip()]
