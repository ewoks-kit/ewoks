from typing import Any
from typing import Dict
from typing import List

from . import _unknown


def pip_freeze_requirements(freeze: List[str]) -> Dict[str, Any]:
    metadata = _unknown.unknown_requirements()
    metadata["manager"] = dict(name="pip", version="", freeze=freeze)
    return metadata
