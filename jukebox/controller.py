import os.path
import threading
import queue
import uuid
import yt_dlp
from just_playback import Playback
from .lyrics import Lyrics
from .song import Song
import time
from django.conf import settings


class Controller:
    def __init__(self, music_dir=None):
        self.music_dir = music_dir or settings.MUSIC_DIR
        self.download_opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmp": "%(title)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
        }

        self.song_queue = queue.Queue()
        self.song_list = []
        self.download_queue = queue.Queue()
        self.download_list = []

        self.playback = Playback()
        self.lyrics = Lyrics()

        threading.Thread(target=self._download_worker, daemon=True).start()
        threading.Thread(target=self._music_worker, daemon=True).start()

        if not os.path.exists(self.music_dir):
            print(f"Creating music directory: {self.music_dir}")
            os.makedirs(self.music_dir, exist_ok=True)

    def _download_worker(self):
        while True:
            if self.download_queue.empty():
                time.sleep(0.1)
                continue

            url = self.download_queue.get()
            self.download_song(url)

            if url in self.download_list:
                self.download_list.remove(url)
            self.download_queue.task_done()

    def queue_entry(self, entry, audio):
        thumbnail = entry.get("thumbnail", "")
        title = entry.get("title", "")
        format = "wav"
        prepared_filename = audio.prepare_filename(entry)
        base_filename = os.path.splitext(prepared_filename)[0]
        file = f"{base_filename}.{format}"
        author = entry.get("channel", "")
        album = entry.get("album", "")
        url = entry.get("url", "")

        song = Song(title=title, author=author, album=album, file=file,
                    format=format, thumbnail=thumbnail, url=url)

        song.lyrics = self.lyrics.get(song)

        self.song_queue.put(song)
        self.song_list.append(song)

    def download_song(self, url):
        try:
            download_opts = self.download_opts.copy()
            download_opts["outtmpl"] = os.path.join(
                self.music_dir, "%(title)s")

            with yt_dlp.YoutubeDL(download_opts) as audio:
                info_dict = audio.extract_info(url, download=True)
                if "entries" in info_dict:
                    for entry in info_dict["entries"]:
                        if not entry:
                            continue
                        self.queue_entry(entry, audio)
                else:
                    self.queue_entry(info_dict, audio)
        except Exception as e:
            print("Unable to download the song:", e)

    def _music_worker(self):
        while True:
            if not self.playback.active:
                song = self.song_queue.get()
                path = song.file
                self.play_song(path)

                while self.playback.active:
                    time.sleep(0.1)

                if song in self.song_list:
                    self.song_list.remove(song)

                file_still_needed = any(s.file == path for s in self.song_list)
                if not file_still_needed and song.url not in self.download_list:
                    try:
                        os.remove(path)
                    except:
                        pass
                self.song_queue.task_done()
            else:
                time.sleep(0.1)

    def play_song(self, path):
        try:
            self.playback.load_file(path)
            self.playback.play()
        except Exception as e:
            print("Unable to play song:", e)

    def play(self, url):
        self.download_queue.put(url)
        self.download_list.append(url)

    def next(self):
        self.playback.stop()

    def stop(self):
        with self.download_queue.mutex:
            self.download_queue.queue.clear()
            self.download_list.clear()

        with self.song_queue.mutex:
            self.song_queue.queue.clear()
            self.song_list.clear()
        self.playback.stop()

        for filename in os.listdir(self.music_dir):
            filepath = os.path.join(self.music_dir, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except:
                print(f"Unable to delete file {filepath}")

    def pause(self):
        if self.playback.paused:
            self.playback.resume()
            return
        self.playback.pause()

    def quit(self):
        print("Quitting...")
        self.stop()

    def is_paused(self):
        return self.playback.paused

    def set_volume(self, new_volume):
        new_volume = max(0.0, min(1.0, new_volume))
        self.playback.set_volume(new_volume)

    def get_active(self):
        return self.playback.active

    def get_volume(self):
        return self.playback.volume

    def get_duration(self):
        return self.playback.duration

    def get_curr_pos(self):
        return self.playback.curr_pos

    def set_curr_pos(self, new_pos):
        duration = self.get_duration()
        new_pos = min(max(0, new_pos), duration)
        self.playback.seek(new_pos)

    def get_lyrics(self):
        if len(self.song_list) == 0:
            return {"lyrics": [], "index": None}

        curr_pos = self.get_curr_pos()
        song = self.song_list[0]
        lyrics = []

        if not song.lyrics:
            return {"lyrics": [], "index": None}

        index = None
        for i in range(len(song.lyrics)):
            lyric = song.lyrics[i]
            if lyric["timestamp"] and lyric["timestamp"] < curr_pos:
                index = i
            lyrics.append(lyric["line"])
        return {"lyrics": lyrics, "index": index}


# Lazy singleton
_controller = None


def get_controller():
    """Get the shared Controller instance, creating it on first access."""
    global _controller
    if _controller is None:
        _controller = Controller()
    return _controller
