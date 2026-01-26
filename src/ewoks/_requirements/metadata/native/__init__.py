import json
import logging
from importlib import metadata
from pathlib import Path
from typing import Generator
from typing import Optional
from typing import Tuple

from . import git
from . import types

logger = logging.getLogger(__name__)


def distributions() -> Generator[types.Distribution, None, None]:
    """
    Yield all installed distributions.
    """
    for dist in metadata.distributions():
        yield distribution_from_metadata(dist)


def distribution_from_metadata(dist: metadata.Distribution) -> types.Distribution:
    name = dist.metadata["Name"]
    version = dist.version

    try:
        installer = dist.read_text("INSTALLER") or ""
        installer = installer.strip()
        if not installer:
            installer = None
    except Exception:
        installer = None

    # PEP 610: Direct URL Origin of installed distributions
    # https://packaging.python.org/en/latest/specifications/direct-url-data-structure/
    git_info = None
    archive_info = None
    try:
        direct_url_text = dist.read_text("direct_url.json")
        direct_url = json.loads(direct_url_text) if direct_url_text else {}
    except Exception:
        direct_url = {}

    from pprint import pprint

    print()
    print("Path:", dist._path)
    pprint(direct_url)
    print("Installer:", installer)

    url = direct_url.get("url", "")
    has_info = False

    if not has_info and "vcs_info" in direct_url:
        vcs_info = direct_url["vcs_info"]
        if vcs_info.get("vcs") == "git":
            commit_id = vcs_info.get("commit_id")
            if commit_id:
                git_info = types.GitInfo(commit=commit_id, remote=url, dirty=False)
                has_info = True

    if not has_info and "dir_info" in direct_url:
        if url.startswith("file://") or "://" not in url:
            path = Path(url.replace("file://", ""))
            if path.exists():
                git_info = git.git_info_from_path(path)
                has_info = git_info is not None

    if not has_info and "archive_info" in direct_url:
        if not url.startswith("file://") and "://" in url:
            archive = direct_url["archive_info"]

            if "hashes" in archive:
                hashes = archive["hashes"]
            elif "hash" in archive:
                # deprecated
                algo, value = archive["hash"].split("=", 1)
                hashes = {algo: value}
            else:
                hashes = {}

            archive_info = types.ArchiveInfo(url=url, hashes=hashes)
            has_info = True

    return types.Distribution(
        name=name,
        version=version,
        git=git_info,
        archive=archive_info,
        installer=installer,
    )


def distribution_to_pip_requirement(
    dist: types.Distribution,
) -> Tuple[str, Optional[str]]:
    """
    Convert a Distribution into a list of strings in a pip requirements file.
    """
    pypi_req = f"{dist.name}=={dist.version}"

    if dist.archive:
        archive_req = f"{dist.name} @ {dist.archive.url}"

        if dist.archive.hashes:
            for algo, value in dist.archive.hashes.items():
                archive_req += f" --hash={algo}:{value}"

        return pypi_req, archive_req

    if dist.git:
        warning_fmt = "Non-reproducible Ewoks workflow requirement: %s@%s %s"
        if dist.git.remote:
            url = git.normalize_git_url(dist.git.remote)

            if dist.git.dirty:
                logger.warning(
                    warning_fmt, dist.name, dist.git.commit, "has uncommited changes"
                )
                suffix = " # DIRTY"
            else:
                suffix = ""

            git_req = f"{dist.name} @ {url}@{dist.git.commit}{suffix}"
        else:
            logger.warning(
                warning_fmt, dist.name, dist.git.commit, "has no remote repository"
            )

            if dist.git.dirty:
                logger.warning(
                    warning_fmt, dist.name, dist.git.commit, "has uncommited changes"
                )
                suffix = f" # DIRTY @ {dist.git.commit}"
            else:
                suffix = f" # @ {dist.git.commit}"

            git_req = f"{pypi_req}{suffix}"

        return pypi_req, git_req

    return pypi_req, None


if __name__ == "__main__":
    for dist in distributions():
        pypi_req, url_req = distribution_to_pip_requirement(dist)
        print("PyPi:", pypi_req)
        print("URL:", url_req)
