import requests
import urllib.parse
from .types import LyricLine


class Lyrics:
    def __init__(self):
        self.url = "https://lrclib.net"

    def _parse_lyrics(self, content):
        synced_lyrics = content.get("syncedLyrics")
        plain_lyrics = content.get("plainLyrics")

        lyrics = []
        if synced_lyrics:
            for line in synced_lyrics.split("\n"):
                try:
                    time_str = line.split(" ")[0][1:-1]
                    timestamp = 60 * int(time_str.split(":")[0]) + float(time_str.split(":")[1])
                    lyrics.append(LyricLine(timestamp=timestamp, line=" ".join(line.split(" ")[1:])))
                except:
                    continue
        elif plain_lyrics:
            for line in plain_lyrics.split("\n"):
                lyrics.append(LyricLine(timestamp=None, line=line))
        return lyrics

    def get(self, song):
        try:
            track_name = urllib.parse.quote(song.title)
            artist_name = urllib.parse.quote(song.author)
            album_name = urllib.parse.quote(song.album)
            response = requests.get(
                f"{self.url}/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}",
                timeout=10
            )

            if response.status_code != 200:
                return []

            return self._parse_lyrics(response.json())
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return []
