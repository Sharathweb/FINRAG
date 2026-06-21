from dataclasses import dataclass, field
from typing import List, Optional, Any
from .status import Status

@dataclass
class DialogRequest:
    request_id: str
    query: str
    session_id: str
    user_id: str
    session: List[dict] = field(default_factory=list)
    stream: bool = False

@dataclass
class DialogResponse:
    status: Status
    answer: str
    title: str = ""
    recommend_topic: str = ""
    chunks: List[str] = field(default_factory=list) # Use a list instead of a string for chunks
