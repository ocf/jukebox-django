import os.path
import threading
import queue
import signal
import sys
import yt_dlp
from just_playback import Playback
import time

class Song:
    def __init__(self, title, author, file, format, thumbnail, url):
        self.title = title
        self.author = author
        self.file = file
        self.format = format
        self.thumbnail = thumbnail
        self.url = url

    # Compare only based on file location
    def __eq__(self, other):
        return (self.file == other.file)

# Class to Control videos
class Controller:
    def __init__(self, music_dir="music"):

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

        # Initialize Ctrl+C handler to close threads properly
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Songs that have been downloaded and are ready to play
        self.song_queue = queue.Queue()
        self.song_list = []  # List of Song objects
        # Songs that need to be downloaded
        self.download_queue = queue.Queue()
        self.download_list = []  # List of urls

        self.playback = Playback()

        threading.Thread(target=self._download_worker, daemon=True).start()
        threading.Thread(target=self._music_worker, daemon=True).start()

        self.music_dir = music_dir
        if not os.path.exists(music_dir):
            print(f"Unable to find music directory {music_dir}, creating it.")
            os.mkdir(self.music_dir)

    def _signal_handler(self, sig, frame):
        self.quit()
        sys.exit(0)

    def _download_worker(self):
        while (True):
            if self.download_queue.empty():
                continue
            
            # Get the next url and download it
            url = self.download_queue.get()
            self.download_song(url)

            # Remove from download queue and list
            if url in self.download_list:
                self.download_list.remove(url)
            self.download_queue.task_done()
    
    def queue_entry(self, entry, audio):
        thumbnail = entry.get("thumbnail", "")
        title = entry.get("title", "")
        format = "wav"  # hardcoded for now
        prepared_filename = audio.prepare_filename(entry)
        base_filename = os.path.splitext(prepared_filename)[0]
        file = f"{base_filename}.{format}"
        author = entry.get("channel", "No Author")
        url = entry.get("url", "")

        song = Song(title=title, author=author, file=file,
                    format=format, thumbnail=thumbnail, url=url)

        # Append the downloaded song to the song queue/list
        self.song_queue.put(song)
        self.song_list.append(song)

    def download_song(self, url):
        try:
            download_opts = self.download_opts
            download_opts["outtmpl"] = os.path.join(
                self.music_dir, "%(title)s")

            with yt_dlp.YoutubeDL(download_opts) as audio:
                info_dict = audio.extract_info(url, download=True)

                if "entries" in info_dict:
                    for entry in info_dict["entries"]:
                        if not entry:
                            continue
                        print(entry)
                        self.queue_entry(entry, audio)
                else:
                    self.queue_entry(info_dict, audio)
        except Exception as e:
            print("Unable to download the song:", e)

    # Feeds songs to song thread

    def _music_worker(self):
        while (True):
            if not self.playback.active:
                song = self.song_queue.get()
                path = song.file
                self.play_song(path)
                
                while self.playback.active:
                    time.sleep(0.1)

                if song in self.song_list:
                    self.song_list.remove(song)

                # If the song is not queued to be played or downloaded in the future, remove it
                if song.url not in self.download_list and song not in self.song_list:
                    os.remove(path)

                self.song_queue.task_done()

    def play_song(self, path):
        try:
            self.playback.load_file(path)
            self.playback.play()

        except Exception as e:
            print("Unable to play song:", e)

    # Queues a url to be downloaded and played
    def play(self, url):
        self.download_queue.put(url)
        self.download_list.append(url)

    # Change to the next song by finishing the current song on the worker thread
    def next(self):
        self.playback.stop()

    # Stop playback of music by deleting all items off the song queue
    def stop(self):
        with self.download_queue.mutex:
            self.download_queue.queue.clear()
            self.download_list.clear()

        with self.song_queue.mutex:
            self.song_queue.queue.clear()
            self.song_list.clear()
        self.playback.stop()

        # Delete any files in the music directory
        for filename in os.listdir(self.music_dir):
            filepath = os.path.join(self.music_dir, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except:
                print(f"Unable to delete file {filepath}")

    # Pause music playback by setting pause_signal to 1
    def pause(self):
        if self.playback.paused:
            self.playback.resume()
            return
        self.playback.pause()

    # Stops queue and writes to cache
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