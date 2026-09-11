"""Dependencies of a TOML manifest: `name = spec` entries in which the
specification is a version constraint, an URL or a git reference.
"""

import json
import logging
from typing import List
from typing import Sequence

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

logger = logging.getLogger(__name__)


def dependency_lines(requirements: Sequence[str]) -> List[str]:
    """Dependency entries for requirements in PEP 508 format."""
    lines = []
    for requirement in requirements:
        try:
            parsed = Requirement(requirement)
        except InvalidRequirement:
            logger.warning("Skip invalid requirement %r", requirement)
            continue
        lines.append(f"{json.dumps(parsed.name)} = {_specification(parsed)}")
    return lines


def _specification(requirement: Requirement) -> str:
    """Version, URL or git reference of a dependency."""
    if requirement.url:
        if requirement.url.startswith("git+"):
            url, _, revision = requirement.url[len("git+") :].rpartition("@")
            if url:
                return f"{{ git = {json.dumps(url)}, rev = {json.dumps(revision)} }}"
            return f"{{ git = {json.dumps(revision)} }}"
        return f"{{ url = {json.dumps(requirement.url)} }}"
    if requirement.specifier:
        return json.dumps(str(requirement.specifier))
    return '"*"'
