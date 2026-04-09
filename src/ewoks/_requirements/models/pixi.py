from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class PixiManagerInfo(BaseManagerInfo):
    name: Literal["pixi"] = "pixi"
    lockfile: str


class PixiRequirements(BaseRequirements):
    manager: PixiManagerInfo
