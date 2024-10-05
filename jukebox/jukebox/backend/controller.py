import yt_dlp
import json
import jsonpickle
import os.path
import pyaudio
import wave
import threading
import queue

CHUNK = 1024


# For multithreading
song_queue = queue.Queue()
stop_lock = threading.Lock()
stop_signal = 0



class SongInfo(object):

    def __init__(self, name, file, plays, url, format):
        self.name = name
        self.file = file
        self.plays = plays
        self.url = url
        self.format = format


def worker():
    global stop_signal, stop_lock

    while (True):
        item = song_queue.get()
        print(f"working on {item.name}")

        with wave.open(item.file, 'rb') as wf:
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
                if stop_signal:
                    stop_lock.acquire()
                    stop_signal = 0
                    stop_lock.release()
                    break
                stream.write(data)

        stream.close()
        p.terminate()

        song_queue.task_done()

# Class to Control videos


class Controller:
    def __init__(self, music_dir="music", music_cache_file="music/music_cache.json"):

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

    def delete_cache(self):
        self.music_cache = []
        os.remove(self.music_cache_file)

    def delete_file(self, name):
        for song in self.music_cache:
            if song.name == name:
                os.remove(song.file)
                self.music_cache.remove(song)
                return

    def write_cache(self):
        with open(self.music_cache_file, "w+") as f:
            json_cache = jsonpickle.encode(self.music_cache)
            f.write(json_cache)

    def find_file_by_url(self, url):
        for song in self.music_cache:
            if (song.url == url):
                return song
        return None

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

    def play_name(self, name):
        song = self.find_file_by_name(name)
        if song == None:
            print("Unable to locate a song with that name.")
            return
        song_queue.put(song)

    def stop(self):
        global stop_signal, stop_lock

        if stop_signal == 1:
            return

        stop_lock.acquire()
        stop_signal = 1
        stop_lock.release()


def input_handler():
    while True:
        command = input("Enter command (download, play, stop, quit): ").strip().lower()

        if command == "download":
            url = input("Enter the youtube url to download: ")
            controller.download(url)

        if command == "play":
            name = input("Enter the name of the file to play: ")
            controller.play_name(name)

        if command == "stop":
            controller.stop()

        if command == "quit":
            controller.stop()
            controller.write_cache()
            break


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    controller = Controller()
    controller.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    input_handler()
    song_queue.join()
