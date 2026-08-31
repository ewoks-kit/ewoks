"""Requirements of the package managers that install from conda channels."""


def python_specifier(python_version: str) -> str:
    """Conda match specification for a python version.

    Only the major and minor version are pinned because a conda channel does not
    build every patch release of python (for example none after end-of-life).
    """
    if not python_version:
        return "*"
    major_minor = ".".join(python_version.split(".")[:2])
    return f"{major_minor}.*"
