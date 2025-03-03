import os.path
import pyaudio
import wave
import threading
import queue
import signal
import sys
import yt_dlp

CHUNK = 1024


class Song:
    def __init__(self, title, file, format):
        self.title = title
        self.file = file
        self.format = format

# Class to Control videos


class Controller:
    def __init__(self, music_dir="music"):
        # Initialize Ctrl+C handler to write to cache before exiting

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

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.song_queue = queue.Queue()
        self.download_queue = queue.Queue()

        self.next_event = threading.Event()
        self.pause_event = threading.Event()

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
            try: 
                url = self.download_queue.get()

                download_opts = self.download_opts
                download_opts["outtmpl"] = os.path.join(self.music_dir, "%(title)s")

                with yt_dlp.YoutubeDL(download_opts) as audio:
                    info_dict = audio.extract_info(url, download=True)

                    title = info_dict["title"]
                    format = "wav"  # hardcoded for now

                    prepared_filename = audio.prepare_filename(info_dict)
                    base_filename = os.path.splitext(prepared_filename)[0]
                    file = f"{base_filename}.{format}"
                    song = Song(title, file, format)
                    self.song_queue.put(song)
            except Exception as e:
                print("Unable to download the song:", e)
            self.download_queue.task_done()

    # Song playback thread function
    def _music_worker(self):
        while (True):
            try:
                item = self.song_queue.get()
                path = item.file
                
                with wave.open(path, 'rb') as wf:
                    p = pyaudio.PyAudio()

                    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=wf.getframerate(),
                                    output=True)

                    while True:
                        if self.next_event.is_set():
                            self.next_event.clear()
                            break
                            
                        if not self.pause_event.is_set():
                            data = wf.readframes(CHUNK)
                            if len(data) == 0:
                                break
                            stream.write(data)
                        else:
                            self.pause_event.wait(0.1)

                stream.close()
                p.terminate()

                os.remove(path)
            except Exception as e:
                print("Unable to play song:", e)

            self.song_queue.task_done()

    def remove(self, song):
        print(f"Trying to remove {song.file}")
        try:
            os.remove(song.file)
        except:
            print("Unable to remove file.")

    # Queues a url to be downloaded and played
    def play(self, url):
        self.download_queue.put(url)

    # Change to the next song by finishing the current song on the worker thread
    def next(self):
        self.next_event.set()

    # Stop playback of music by deleting all items off the song queue
    def stop(self):
        with self.download_queue.mutex:
            self.download_queue.queue.clear()

        with self.song_queue.mutex:
            self.song_queue.queue.clear()
        self.next()

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
        if self.pause_event.is_set():
            self.pause_event.clear()
            return
        self.pause_event.set()

    # Stops queue and writes to cache
    def quit(self):
        print("Quitting...")
        self.stop()

