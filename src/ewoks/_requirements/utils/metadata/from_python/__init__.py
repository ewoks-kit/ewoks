import json
import logging
import platform
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from typing import Any
from typing import Dict

from .. import models
from . import _git

logger = logging.getLogger(__name__)


@lru_cache(1)
def current_requirements() -> Dict[str, Any]:
    """
    Return installed python distributions.
    """
    distributions = [
        _distribution_from_metadata(dist) for dist in metadata.distributions()
    ]
    return dict(
        system=_system_metadata(),
        python=_python_metadata(),
        distributions=distributions,
    )


def _system_metadata() -> Dict[str, Any]:
    uname = platform.uname()
    return dict(
        system=uname.system,
        release=uname.release,
        version=uname.version,
        machine=uname.machine,
        processor=uname.processor,
    )


def _python_metadata() -> Dict[str, Any]:
    return dict(
        version=platform.python_version(),
        implementation=platform.python_implementation(),
        compiler=platform.python_compiler(),
        build=", ".join(platform.python_build()),
    )


def _distribution_from_metadata(
    dist: metadata.Distribution,
) -> models.Distribution:
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

    url = direct_url.get("url", "")
    has_info = False

    if not has_info and "vcs_info" in direct_url:
        vcs_info = direct_url["vcs_info"]
        if vcs_info.get("vcs") == "git":
            commit_id = vcs_info.get("commit_id")
            if commit_id:
                git_info = models.GitInfo(
                    commit=commit_id, remote=url, uncommitted_changes=False
                )
                has_info = True

    if not has_info and "dir_info" in direct_url:
        if url.startswith("file://") or "://" not in url:
            path = Path(url.replace("file://", ""))
            if path.exists():
                git_info = _git.git_info_from_path(path)
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

            archive_info = models.ArchiveInfo(url=url, hashes=hashes)
            has_info = True

    return models.Distribution(
        name=name,
        version=version,
        git=git_info,
        archive=archive_info,
        installer=installer,
    )
