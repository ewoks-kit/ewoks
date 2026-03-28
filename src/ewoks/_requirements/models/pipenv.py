from typing import List
from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class PipenvManagerInfo(BaseManagerInfo):
    name: Literal["pipenv"] = "pipenv"
    requirements: List[str]


class PipenvRequirements(BaseRequirements):
    manager: PipenvManagerInfo

    def __info__(self) -> str:
        requirements = "\n  ".join(self.manager.requirements)
        return f"{super().__info__()}\nRequirements:\n  {requirements}"
