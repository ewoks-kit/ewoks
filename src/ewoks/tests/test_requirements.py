import pytest

from .._requirements.pip.sanitize import sanitize_requirements


def test_normal_requirement():
    req = ["ewoks==1.1.0"]
    sanitized, warnings = sanitize_requirements(req)
    assert sanitized == ["ewoks==1.1.0"]
    assert warnings == []


def test_editable_ssh_vcs_url_normalized():
    ssh_project_name = "querypool"
    ssh_project_url = "gitlab.esrf.fr/dau/querypool.git"
    ssh_project_commit = "ab6acc7e140ed33eb896b1336a5a5aac6b60cc0f"
    req = [
        f"-e git+ssh://git@{ssh_project_url}@{ssh_project_commit}#egg={ssh_project_name}"
    ]

    sanitized, warnings = sanitize_requirements(req)

    expected_sanitized = [
        f"{ssh_project_name} @ git+https://{ssh_project_url}@{ssh_project_commit}"
    ]
    expected_warnings = [
        f"Normalize VCS requirement 'git+ssh://git@{ssh_project_url}@{ssh_project_commit}#egg={ssh_project_name}' "
        f"to '{ssh_project_name} @ git+ssh://git@{ssh_project_url}@{ssh_project_commit}'",
        f"Normalize requirement '{ssh_project_name} @ git+ssh://git@{ssh_project_url}@{ssh_project_commit}' "
        f"to '{ssh_project_name} @ git+https://{ssh_project_url}@{ssh_project_commit}'",
    ]

    assert sanitized == expected_sanitized
    assert warnings == expected_warnings


@pytest.mark.parametrize("exists", [True, False])
def test_editable_local_path_with_comment_replacement(tmp_path, exists):
    path = tmp_path / "repo_name"
    if exists:
        path.mkdir()

    comment = "# Editable Git install with no remote (project_name==1.0.0)"
    replacement = "project_name==1.0.0"
    req = [comment, f"-e {path}"]

    sanitized, warnings = sanitize_requirements(req)

    assert sanitized == [replacement]
    assert warnings == [f"Replaced editable install '{path}' with '{replacement}'."]


@pytest.mark.parametrize("exists", [True, False])
def test_editable_local_path_without_comment_replacement(tmp_path, exists):
    path = tmp_path / "repo_name"
    if exists:
        path.mkdir()
        warning = f"Editable path exists locally: '{path}'"
    else:
        warning = f"Editable path does not exist locally: '{path}'"

    req = [f"-e {path}"]

    sanitized, warnings = sanitize_requirements(req)

    assert sanitized == [f"-e {path}"]
    if exists:
        assert warnings == [warning]
    else:
        assert warnings == [warning]


def test_branch_specified_requirement():
    project_name = "ewoksutils"
    project_url = "gitlab.esrf.fr/workflow/ewoks/ewoksutils.git"
    project_branch = "main"

    req = [f"{project_name}@ git+https://{project_url}@{project_branch}"]

    sanitized, warnings = sanitize_requirements(req)

    # No warnings expected here (assuming valid format)
    assert sanitized == [f"{project_name}@ git+https://{project_url}@{project_branch}"]
    assert warnings == []


def test_invalid_requirement_warning():
    project_url = "gitlab.esrf.fr/workflow/ewoks/ewoksutils.git"

    req = [f"git+https://{project_url}"]

    sanitized, warnings = sanitize_requirements(req)

    assert sanitized == [f"git+https://{project_url}"]
    assert any("Possibly invalid requirement format" in w for w in warnings)
