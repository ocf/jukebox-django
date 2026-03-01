from dataclasses import dataclass
from typing import List, Optional
from .song import Song
from .time import TimeState
from .lyrics import LyricsState

@dataclass
class JukeboxState:
    volume: float
    status: str
    time: TimeState
    now_playing: Optional[Song]
    queue: List[Song]
    lyrics: LyricsState
