import platform
from functools import lru_cache
from typing import Any
from typing import Dict

from . import installed


@lru_cache
def current_requirements() -> Dict[str, Any]:
    return dict(
        system=_system_metadata(),
        python=_python_metadata(),
        distributions=installed.distributions(),
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
