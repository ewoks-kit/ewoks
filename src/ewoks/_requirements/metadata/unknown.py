from functools import lru_cache


@lru_cache
def unknown_metadata() -> dict:
    return dict(
        system=_unknown_system_metadata(),
        python=_unknown_python_metadata(),
    )


def _unknown_system_metadata() -> dict:
    return dict(
        system="unknown",
        release="unknown",
        version="unknown",
        machine="unknown",
        processor="unknown",
    )


def _unknown_python_metadata() -> dict:
    return dict(
        version="unknown",
        implementation="unknown",
        compiler="unknown",
        build="unknown",
    )
