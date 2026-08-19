from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class SystemInfo(BaseModel):
    system: str = Field(description="Operating system name.", examples=["Linux"])
    release: str = Field(
        description="Operating system release.", examples=["5.15.0-139-generic"]
    )
    version: str = Field(
        description="Operating system version.",
        examples=["#149-Ubuntu SMP Fri Apr 11 19:19:52 UTC 2025"],
    )
    machine: str = Field(description="Machine type.", examples=["x86_64"])
    processor: str = Field(description="Processor name.", examples=["x86_64"])


class PythonInfo(BaseModel):
    version: str = Field(description="Python version.", examples=["3.12.11"])
    implementation: str = Field(
        description="Python implementation.", examples=["CPython"]
    )
    compiler: str = Field(
        description="Compiler used to build python.", examples=["GCC 11.4.0"]
    )
    build: str = Field(
        description="Build number and date of the python interpreter.",
        examples=["main, Jun 11 2025 10:57:12"],
    )


class GitInfo(BaseModel):
    commit: str = Field(
        description="Commit from which the distribution was installed.",
        examples=["249ea97730a0134de4ecd1b7f136cc48bc0ec2de"],
    )
    remote: Optional[str] = Field(
        default=None,
        description=(
            "Repository from which the distribution was installed. Without a "
            "repository the distribution cannot be installed elsewhere."
        ),
        examples=["https://github.com/ewoks-kit/ewokscore.git"],
    )
    uncommitted_changes: bool = Field(
        default=False,
        description=(
            "The repository had uncommitted changes, so the commit does not "
            "describe the installed distribution completely."
        ),
        examples=[False],
    )


class ArchiveInfo(BaseModel):
    url: str = Field(
        description="Archive from which the distribution was installed.",
        examples=["https://host/ewokscore-5.1.0-py3-none-any.whl"],
    )
    hashes: Dict[str, str] = Field(
        description="Hashes of the archive, by algorithm name.",
        examples=[{"sha256": "5f8e9c1a"}],
    )


class Distribution(BaseModel):
    name: str = Field(description="Distribution name.", examples=["ewokscore"])
    version: str = Field(
        description="Distribution version, empty when unknown.", examples=["5.1.0"]
    )
    git: Optional[GitInfo] = Field(
        default=None,
        description="Set when the distribution was installed from a git repository.",
    )
    archive: Optional[ArchiveInfo] = Field(
        default=None,
        description="Set when the distribution was installed from an archive.",
    )
    installer: Optional[str] = Field(
        default=None,
        description="Tool that installed the distribution.",
        examples=["pip"],
    )
