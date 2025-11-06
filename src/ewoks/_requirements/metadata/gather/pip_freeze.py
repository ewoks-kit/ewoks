from typing import Any
from typing import Dict
from typing import List

from . import unknown


def pip_freeze_requirements(freeze: List[str]) -> Dict[str, Any]:
    metadata = unknown.unknown_requirements()
    metadata["manager"] = dict(name="pip", version="", freeze=freeze)
    return metadata
