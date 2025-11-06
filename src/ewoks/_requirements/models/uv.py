from typing import List
from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class UvManagerInfo(BaseManagerInfo):
    name: Literal["uv"] = "uv"
    requirements: List[str]


class UvRequirements(BaseRequirements):
    manager: UvManagerInfo

    def __info__(self) -> str:
        requirements = "\n  ".join(self.manager.requirements)
        return f"{super().__info__()}\nRequirements:\n  {requirements}"
