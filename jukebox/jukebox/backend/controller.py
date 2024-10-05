# Honestly would have been easier with rust
import yt_dlp
import json
import jsonpickle
import os.path
import pyaudio
import wave
import threading
import queue

CHUNK = 1024


class SongInfo(object):
    def __init__(self, name, file, plays, url, format):
        self.name = name
        self.file = file
        self.plays = plays
        self.url = url
        self.format = format

# Class to Control videos

class Controller:
    def __init__(self, music_dir="music", music_cache_file="music/music_cache.json"):
        self.song_queue = queue.Queue()

        self.next_lock = threading.Lock()
        self.next_signal = 0
        self.pause_lock = threading.Lock()
        self.pause_signal = 0

        threading.Thread(target=self._music_worker, daemon=True).start()

        self.download_opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
        }

        self.music_dir = music_dir
        self.music_cache_file = music_cache_file
        self.music_cache = []

        if not os.path.exists(music_dir):
            os.makedirs(music_dir)

        if os.path.exists(music_cache_file):
            with open(music_cache_file, "r") as f:
                try:
                    json_cache = f.read()
                    self.music_cache = jsonpickle.decode(json_cache)
                except json.JSONDecodeError:
                    self.music_cache = []
        else:
            print(f"Could not find {self.music_cache_file}, creating it.")
            with open(music_cache_file, "w") as f:
                json.dump([], f)

    # Song playback thread function
    def _music_worker(self):
        while (True):
            item = self.song_queue.get()
            print(f"working on {item.name}")

            with wave.open(item.file, 'rb') as wf:
                p = pyaudio.PyAudio()

                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)

                while True:
                    if self.next_signal:
                        self.next_lock.acquire()
                        self.next_signal = 0
                        self.next_lock.release()
                        break

                    if self.pause_signal:
                        continue

                    data = wf.readframes(CHUNK)
                    if len(data) == 0:
                        break
                    stream.write(data)

            stream.close()
            p.terminate()

            self.song_queue.task_done()

    # Delete all songs from the cache
    def delete_cache(self):
        for song in self.music_cache:
            os.remove(song.file)
        self.music_cache = []
        os.remove(self.music_cache_file)

    # Delete a file by its name
    def delete_file(self, name):
        song = self.find_file_by_name(name)
        os.remove(song.file)
        self.music_cache.remove(song)
        return

    # Write to the song cache
    def write_cache(self):
        with open(self.music_cache_file, "w+") as f:
            json_cache = jsonpickle.encode(self.music_cache)
            f.write(json_cache)

    # Find the SongInfo by its url, otherwise return None
    def find_file_by_url(self, url):
        for song in self.music_cache:
            if (song.url == url):
                return song
        return None

    # Find the SongInfo by its name, otherwise return None
    def find_file_by_name(self, name):
        for song in self.music_cache:
            if (song.name == name):
                return song
        return None

    # Download music from a url
    def download(self, url):
        if self.find_file_by_url(url):
            return

        download_opts = self.download_opts
        download_opts["outtmpl"] = os.path.join(
            self.music_dir, "%(title)s")

        with yt_dlp.YoutubeDL(download_opts) as audio:
            info_dict = audio.extract_info(url, download=True)

            title = info_dict["title"]
            format = "wav"  # hardcoded for now
            filename = f"{audio.prepare_filename(info_dict)}.{format}"
            print(filename)
            self.music_cache.append(SongInfo(title, filename, 0, url, format))

    # Play a song by its name (normally file name without extension)
    def play(self, name):
        song = self.find_file_by_name(name)
        if song == None:
            print("Unable to locate a song with that name.")
            return
        self.song_queue.put(song)
        song.plays += 1

    # Change to the next song by finishing the current song on the worker thread
    def next(self):
        if self.next_signal == 1:
            return

        self.next_lock.acquire()
        self.next_signal = 1
        self.next_lock.release()

    # Stop playback of music by deleting all items off the song queue
    def stop(self):
        with self.song_queue.mutex:
            self.song_queue.queue.clear()
        self.next()

    # Pause music playback by setting pause_signal to 1
    def pause(self):
        # Already paused
        self.pause_lock.acquire()
        self.pause_signal = 0 if self.pause_signal else 1
        self.pause_lock.release()


def input_handler(controller):
    while True:
        command = input(
            "Enter command (download, play, next, stop, pause, quit): ").strip().lower()

        if command == "download":
            url = input("Enter the youtube url to download: ")
            controller.download(url)

        if command == "play":
            name = input("Enter the name of the file to play: ")
            controller.play(name)

        if command == "next":
            controller.next()

        if command == "stop":
            controller.stop()

        if command == "pause":
            controller.pause()

        if command == "quit":
            controller.stop()
            controller.write_cache()
            break

    controller.song_queue.join()


if __name__ == "__main__":
    controller = Controller()
    input_handler(controller)
