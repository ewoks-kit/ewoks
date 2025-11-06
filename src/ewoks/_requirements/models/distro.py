from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class GitInfo(BaseModel):
    commit: str
    remote: Optional[str] = None
    uncomitted_changes: bool = Field(default=False, description="Uncommited changes")


class ArchiveInfo(BaseModel):
    url: str
    hashes: Dict[str, str]


class Distribution(BaseModel):
    name: str
    version: str
    git: Optional[GitInfo] = None
    archive: Optional[ArchiveInfo] = None
    installer: Optional[str] = None
