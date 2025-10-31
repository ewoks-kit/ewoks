import os
import re
from typing import List
from typing import Sequence
from typing import Tuple
from urllib.parse import ParseResult
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import urlunparse

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement


def sanitize_requirements(requirements: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Sanitize a list of requirements coming from 'pip freeze'.
    Returns a sanitized with warnings regarding applied changes.
    """
    sanitized = []
    warnings = []
    previous_comment = ""

    for requirement in requirements:
        requirement = requirement.strip()
        if not requirement:
            continue
        if requirement.startswith("#"):
            previous_comment = requirement
            continue

        editable = requirement.startswith("-e ")
        if editable:
            requirement = requirement[2:].strip()

        if editable and _is_path(requirement):
            requirement, warning = _handle_editable_path(requirement, previous_comment)
            if warning:
                warnings.append(warning)
            if _is_path(requirement):
                sanitized.append(f"-e {requirement}")
                continue

        requirement, warning = _normalize_vcs_url(requirement)
        if warning:
            warnings.append(warning)

        requirement, warning = _normalize_requirement(requirement)
        if warning:
            warnings.append(warning)

        sanitized.append(requirement)
        previous_comment = ""

    return sanitized, warnings


def _is_path(requirement: str) -> bool:
    """Return True if requirement looks like a local path (not a URL)."""
    return "://" not in requirement and ("/" in requirement or "\\" in requirement)


def _normalize_requirement(requirement: str) -> Tuple[str, str]:
    """Normalize the requirement or pass-through with warning when not valid."""
    try:
        req = Requirement(requirement)
    except InvalidRequirement:
        warning = f"Possibly invalid requirement format: {requirement!r}"
        return requirement, warning

    replacement = _format_requirement(req)
    if requirement.replace(" ", "") != replacement.replace(" ", ""):
        warning = f"Normalize requirement {requirement!r} to {replacement!r}"
        return replacement, warning

    return requirement, ""


def _format_requirement(req: Requirement) -> str:
    """Convert requirement to a string and replace ssh with https"""
    if req.url and req.url.startswith("git+ssh://"):
        https_url = re.sub(r"^git\+ssh://git@", "git+https://", req.url)
        return f"{req.name} @ {https_url}"
    return str(req)


def _normalize_vcs_url(requirement: str) -> Tuple[str, str]:
    """Normalize VCS URLs to the PEP 508 spec (name @ url)."""
    parsed = urlparse(requirement)

    if not parsed.fragment or "egg=" not in parsed.fragment:
        return requirement, ""

    qs = parse_qs(parsed.fragment)
    egg_names = qs.get("egg")
    if not egg_names:
        return requirement, ""

    egg_name = egg_names[0]
    base_url = _remove_url_fragment(parsed)
    new_requirement = f"{egg_name} @ {base_url}"
    warning = f"Normalize VCS requirement '{requirement}' to '{new_requirement}'"
    return new_requirement, warning


def _remove_url_fragment(parsed: ParseResult) -> str:
    return urlunparse(
        ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=parsed.path,
            params=parsed.params,
            query=parsed.query,
            fragment="",
        )
    )


def _handle_editable_path(requirement: str, comment: str) -> Tuple[str, str]:
    """Replace editable path with comment substitution if available."""
    replacement = _requirement_from_comment(comment)
    if replacement:
        warning = f"Replaced editable install '{requirement}' with '{replacement}'."
        return replacement, warning
    if os.path.exists(requirement):
        warning = f"Editable path exists locally: '{requirement}'"
    else:
        warning = f"Editable path does not exist locally: '{requirement}'"
    return requirement, warning


_REQUIREMENT_COMMENT_RE = re.compile(r"\(([\w\.\-\[\]]+[=><!~]=[\w\.\-]+)\)")


def _requirement_from_comment(comment: str) -> str:
    """Extract requirement from a 'pip freeze' comment."""
    # When doing "pip freeze" in the same envrinment where "git status" gives this
    #   fatal: detected dubious ownership in repository at '/path/to/repo'
    # the requirements list will contain "-e /path/to/repo" with a warning that
    # contains a requirement message.
    match = _REQUIREMENT_COMMENT_RE.search(comment)
    if match:
        return match.group(1)
    return ""
