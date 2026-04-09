from typing import List

from pydantic import BaseModel

from .distro import Distribution


class SystemInfo(BaseModel):
    system: str
    release: str
    version: str
    machine: str
    processor: str


class PythonInfo(BaseModel):
    version: str
    implementation: str
    compiler: str
    build: str


class BaseManagerInfo(BaseModel):
    name: str
    version: str


class BaseRequirements(BaseModel):
    system: SystemInfo
    python: PythonInfo
    distributions: List[Distribution]
    manager: BaseManagerInfo

    def __info__(self) -> str:
        return (
            f"Manager: {self.manager.name} ({self.manager.version}) "
            f"python={self.python.version}) "
            f"distributions={len(self.distributions)}"
        )
