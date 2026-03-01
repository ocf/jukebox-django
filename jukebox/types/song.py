from dataclasses import dataclass, field
from typing import List, Optional
import uuid
from .lyrics import LyricLine

@dataclass
class Song:
    title: str
    author: str
    album: str
    file: str
    format: str
    thumbnail: str
    url: str
    id: uuid.UUID
    lyrics: Optional[List[LyricLine]] = None

    def __eq__(self, other):
        if not isinstance(other, Song):
            return False
        return self.id == other.id
