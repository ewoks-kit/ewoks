from typing import Literal

from pydantic import BaseModel


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
    schema_version: Literal["1.0"] = "1.0"
    manager: BaseManagerInfo
    system: SystemInfo
    python: PythonInfo

    def __info__(self) -> str:
        return (
            f"Manager: {self.manager.name} ({self.manager.version}) "
            f"python={self.python.version})"
        )
