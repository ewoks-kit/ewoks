from typing import List
from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class PipManagerInfo(BaseManagerInfo):
    name: Literal["pip"] = "pip"
    freeze: List[str]


class PipRequirements(BaseRequirements):
    manager: PipManagerInfo

    def __info__(self) -> str:
        freeze = "\n  ".join(self.manager.freeze)
        return f"{super().__info__()}\nRequirements:\n  {freeze}"
