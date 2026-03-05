import platform
from functools import lru_cache


@lru_cache
def current_metadata() -> dict:
    return dict(
        system=_system_metadata(),
        python=_python_metadata(),
    )


def _system_metadata() -> dict:
    uname = platform.uname()
    return dict(
        system=uname.system,
        release=uname.release,
        version=uname.version,
        machine=uname.machine,
        processor=uname.processor,
    )


def _python_metadata() -> dict:
    return dict(
        version=platform.python_version(),
        implementation=platform.python_implementation(),
        compiler=platform.python_compiler(),
        build=", ".join(platform.python_build()),
    )
