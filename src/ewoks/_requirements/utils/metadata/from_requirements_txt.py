from typing import Any
from typing import Dict
from typing import List

from .. import requirements_txt
from . import _unknown


def requirements_txt_metadata(requirements: List[str]) -> Dict[str, Any]:
    """Requirements for a legacy requirements list in `requirements.txt` format.

    The requirements are parsed into python distributions so that any package
    manager can reproduce the environment, not only the one that installs a
    `requirements.txt` file.
    """
    metadata = dict(_unknown.unknown_requirements())
    metadata["distributions"] = [
        distribution
        for distribution in map(
            requirements_txt.distribution_from_requirement,
            requirements_txt.sanitize(requirements),
        )
        if distribution is not None
    ]
    metadata["manager"] = dict(
        name="pip-venv",
        version="",
        files={requirements_txt.REQUIREMENTS_FILENAME: "\n".join(requirements)},
    )
    return metadata
