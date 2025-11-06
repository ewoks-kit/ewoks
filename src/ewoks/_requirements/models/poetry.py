from typing import List
from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class PoetryManagerInfo(BaseManagerInfo):
    name: Literal["poetry"] = "pip"
    requirements: List[str]


class PoetryRequirements(BaseRequirements):
    manager: PoetryManagerInfo
