import requests
import urllib

class Lyrics:
    def __init__(self):
        self.url = "https://lrclib.net"
    
    def _parse_lyrics(self, content):
        synced_lyrics = content.get("syncedLyrics")
        plain_lyrics = content.get("syncedLyrics")
        
        lyrics = []
        if synced_lyrics:
            # Parse
            for line in synced_lyrics.split("\n"):
                time_str = line.split(" ")[0][1:-2]
                timestamp = 60 * int(time_str.split(":")[0]) + float(time_str.split(":")[1])
                lyrics.append({"timestamp": timestamp, "line": " ".join(line.split(" ")[1:])})
        elif plain_lyrics:
            for line in plain_lyrics.split("\n"):
                lyrics.append({"timestamp": None, "line": line})
        return lyrics
        
    def get(self, song):
        track_name = urllib.parse.quote(song.title)
        artist_name= urllib.parse.quote(song.author)
        album_name = urllib.parse.quote(song.album)
        response = requests.get(f"{self.url}/api/get?artist_name={artist_name}&track_name={track_name}&album_name={album_name}")

        if (response.status_code != 200):
            return []

        return self._parse_lyrics(response.json())