from functools import lru_cache
from typing import Any
from typing import Dict


@lru_cache
def unknown_requirements() -> Dict[str, Any]:
    return dict(
        system=_unknown_system_metadata(),
        python=_unknown_python_metadata(),
        distributions=list(),
    )


def _unknown_system_metadata() -> Dict[str, Any]:
    return dict(
        system="",
        release="",
        version="",
        machine="",
        processor="",
    )


def _unknown_python_metadata() -> Dict[str, Any]:
    return dict(
        version="",
        implementation="",
        compiler="",
        build="",
    )
