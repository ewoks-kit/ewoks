from typing import Dict
from typing import NamedTuple
from typing import Optional


class GitInfo(NamedTuple):
    commit: str
    remote: Optional[str]
    dirty: bool


class ArchiveInfo(NamedTuple):
    url: str
    hashes: Dict[str, str]


class Distribution(NamedTuple):
    name: str
    version: str
    git: Optional[GitInfo]
    archive: Optional[ArchiveInfo]
    installer: Optional[str]
