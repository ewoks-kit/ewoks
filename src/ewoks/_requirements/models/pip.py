from typing import List
from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class PipManagerInfo(BaseManagerInfo):
    name: Literal["pip"] = "pip"
    requirements: List[str]


class PipRequirements(BaseRequirements):
    manager: PipManagerInfo

    def __info__(self) -> str:
        requirements = "\n  ".join(self.manager.requirements)
        return f"{super().__info__()}\nRequirements:\n  {requirements}"
