import os.path
import pyaudio
import wave
import threading
import queue
import signal
import sys
import config
import json
import asyncio
import websockets
from websockets.asyncio.server import serve

CHUNK = 1024

# Class to Control videos
class Controller:
    def __init__(self, music_dir="/tmp"):
        # Initialize Ctrl+C handler to write to cache before exiting

        signal.signal(signal.SIGINT, self._signal_handler)

        self.song_queue = queue.Queue()

        self.next_lock = threading.Lock()
        self.next_signal = 0
        self.pause_lock = threading.Lock()
        self.pause_signal = 0

        threading.Thread(target=self._music_worker, daemon=True).start()

        self.music_dir = music_dir
        self.music_cache = []

        if not os.path.exists(music_dir):
            os.makedirs(music_dir)

    def _signal_handler(self, sig, frame):
        self.quit()
        sys.exit(0)

    # Song playback thread function
    def _music_worker(self):
        while (True):
            item = self.song_queue.get()
            print(f"working on {item['title']}")
            path = os.path.join(self.music_dir, item["file"])
            with wave.open(path, 'rb') as wf:
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
            
            os.remove(path)

            self.song_queue.task_done()
    
    # Play a song by its name (normally file name without extension)
    def play(self, song):
        self.song_queue.put(song)

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

    # Stops queue and writes to cache
    def quit(self):
        print("Quitting...")
        self.stop()


async def handler(websocket):
    controller = Controller(music_dir="music")
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break

        if message == "queue":
            print("Queuing...")
            song = await websocket.recv()
            song = json.loads(song)

            file = song["file"]
            path = os.path.join(controller.music_dir, file)

            with open(path, "wb+") as f:
                data = await websocket.recv()
                while (data != "finished"):
                    f.write(data)
                    data = await websocket.recv()
            
            controller.play(song)
            

        if message == "next":
            controller.next()

        if message == "stop":
            controller.stop()

        if message == "pause":
            controller.pause()

        if message == "quit":
            controller.quit()
            break

    controller.song_queue.join()


async def main():
    async with serve(handler, "", config.PORT):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
