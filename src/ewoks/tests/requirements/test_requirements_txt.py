"""Tests of the `requirements.txt` format."""

import pytest

from ..._requirements.utils import requirements_txt
from ..._requirements.utils.metadata import models
from .utils import DISTRIBUTIONS
from .utils import REQUIREMENTS


def test_normal_requirement(caplog):
    assert requirements_txt.sanitize(["ewoks==1.1.0"]) == ["ewoks==1.1.0"]
    assert not caplog.text


def test_editable_ssh_vcs_url_normalized(caplog):
    ssh_project_name = "querypool"
    ssh_project_url = "gitlab.esrf.fr/dau/querypool.git"
    ssh_project_commit = "ab6acc7e140ed33eb896b1336a5a5aac6b60cc0f"
    requirement = f"-e git+ssh://git@{ssh_project_url}@{ssh_project_commit}#egg={ssh_project_name}"

    sanitized = requirements_txt.sanitize([requirement])

    assert sanitized == [
        f"{ssh_project_name} @ git+https://{ssh_project_url}@{ssh_project_commit}"
    ]
    assert (
        f"Normalize VCS requirement 'git+ssh://git@{ssh_project_url}@{ssh_project_commit}"
        f"#egg={ssh_project_name}'" in caplog.text
    )
    assert "to 'querypool @ git+https" in caplog.text


@pytest.mark.parametrize("exists", [True, False])
def test_editable_local_path_with_comment_replacement(tmp_path, caplog, exists):
    path = tmp_path / "repo_name"
    if exists:
        path.mkdir()

    comment = "# Editable Git install with no remote (project_name==1.0.0)"
    replacement = "project_name==1.0.0"

    sanitized = requirements_txt.sanitize([comment, f"-e {path}"])

    assert sanitized == [replacement]
    assert f"Replaced editable install '{path}' with '{replacement}'." in caplog.text


@pytest.mark.parametrize("exists", [True, False])
def test_editable_local_path_without_comment_replacement(tmp_path, caplog, exists):
    path = tmp_path / "repo_name"
    if exists:
        path.mkdir()
        warning = f"Editable path exists locally: '{path}'"
    else:
        warning = f"Editable path does not exist locally: '{path}'"

    sanitized = requirements_txt.sanitize([f"-e {path}"])

    assert sanitized == [f"-e {path}"]
    assert warning in caplog.text


def test_branch_specified_requirement(caplog):
    project_name = "ewoksutils"
    project_url = "github.com/ewoks-kit/ewoksutils.git"
    requirement = f"{project_name}@ git+https://{project_url}@main"

    assert requirements_txt.sanitize([requirement]) == [requirement]
    assert not caplog.text


def test_invalid_requirement_warning(caplog):
    requirement = "git+https://github.com/ewoks-kit/ewoksutils.git"

    assert requirements_txt.sanitize([requirement]) == [requirement]
    assert "Possibly invalid requirement format" in caplog.text


def test_distributions_requirements():
    distributions = [
        *DISTRIBUTIONS,
        models.Distribution(
            name="mypackage1",
            version="1.0",
            git=models.GitInfo(commit="123", remote="https://host/group/repo.git"),
        ),
        models.Distribution(
            name="mypackage2",
            version="1.0",
            archive=models.ArchiveInfo(
                url="https://host/mypackage2-1.0-py3-none-any.whl",
                hashes={"sha256": "123"},
            ),
        ),
    ]

    assert requirements_txt.distributions_requirements(distributions) == [
        *REQUIREMENTS,
        "mypackage1 @ git+https://host/group/repo.git@123",
        # The hash is a URL fragment: pip requires a hash for every requirement as
        # soon as one is provided as a '--hash' option
        "mypackage2 @ https://host/mypackage2-1.0-py3-none-any.whl#sha256=123",
    ]
    assert requirements_txt.manifest_requirements(
        distributions
    ) == requirements_txt.distributions_requirements(distributions)
    assert requirements_txt.version_constraints(distributions) == [
        *REQUIREMENTS,
        "mypackage1==1.0",
        "mypackage2==1.0",
    ]


def test_manifest_requirements_unique():
    """A package manager manifest cannot contain the same dependency twice."""
    # The same distributions, but named differently and with another version
    duplicates = [
        dist.model_copy(update={"name": dist.name.upper(), "version": "0.0.1"})
        for dist in DISTRIBUTIONS
    ]
    distributions = DISTRIBUTIONS + duplicates

    assert requirements_txt.manifest_requirements(distributions) == REQUIREMENTS


def test_manifest_requirements_without_comments():
    """Warnings that `pip freeze` adds as comments are not requirements."""
    distributions = [
        models.Distribution(
            name="mypackage", version="1.0", git=models.GitInfo(commit="123")
        )
    ]

    requirements = requirements_txt.distributions_requirements(distributions)
    assert requirements[0].startswith("# ")

    assert requirements_txt.manifest_requirements(distributions) == ["mypackage==1.0"]


@pytest.mark.parametrize(
    "requirement,expected",
    [
        *(
            (
                f"{dist.name}=={dist.version}",
                {"name": dist.name, "version": dist.version},
            )
            for dist in DISTRIBUTIONS
        ),
        ("mypackage", {"name": "mypackage", "version": ""}),
        ("mypackage>=1.0", {"name": "mypackage", "version": ""}),
        (
            "mypackage @ git+https://host/repo.git@123",
            {
                "name": "mypackage",
                "version": "",
                "git": {
                    "commit": "123",
                    "remote": "https://host/repo.git",
                    "uncommitted_changes": False,
                },
            },
        ),
        (
            "mypackage @ https://host/mypackage-1.0.tar.gz",
            {
                "name": "mypackage",
                "version": "",
                "archive": {"url": "https://host/mypackage-1.0.tar.gz", "hashes": {}},
            },
        ),
        (
            "mypackage @ https://host/mypackage-1.0.tar.gz#sha256=123",
            {
                "name": "mypackage",
                "version": "",
                "archive": {
                    "url": "https://host/mypackage-1.0.tar.gz",
                    "hashes": {"sha256": "123"},
                },
            },
        ),
        (
            # Only the hashes are taken out of the fragment
            "mypackage @ https://host/repo.tar.gz#sha256=123&subdirectory=sub",
            {
                "name": "mypackage",
                "version": "",
                "archive": {
                    "url": "https://host/repo.tar.gz#subdirectory=sub",
                    "hashes": {"sha256": "123"},
                },
            },
        ),
        (
            # A git URL without revision cannot be split
            "mypackage @ git+https://host/repo.git",
            {
                "name": "mypackage",
                "version": "",
                "archive": {"url": "git+https://host/repo.git", "hashes": {}},
            },
        ),
    ],
)
def test_distribution_from_requirement(requirement, expected):
    distribution = requirements_txt.distribution_from_requirement(requirement)

    assert distribution is not None
    assert distribution.model_dump(exclude_none=True) == expected


def test_distribution_from_invalid_requirement(caplog):
    assert (
        requirements_txt.distribution_from_requirement("git+https://host/repo") is None
    )
    assert "Skip invalid requirement" in caplog.text
