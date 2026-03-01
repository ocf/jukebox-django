from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LyricLine:
    timestamp: Optional[float]
    line: str

@dataclass
class LyricsState:
    lyrics: List[str]
    index: Optional[int]
