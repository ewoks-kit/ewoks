from typing import Literal

from .base import BaseManagerInfo
from .base import BaseRequirements


class CondaManagerInfo(BaseManagerInfo):
    name: Literal["conda"] = "conda"


class CondaRequirements(BaseRequirements):
    manager: CondaManagerInfo
    environment: dict
