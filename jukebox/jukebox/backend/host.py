import os.path
import yt_dlp
import config
import json
from websockets.sync.client import connect

FILE_CHUNK = 1024


class Host:
    def __init__(self, music_dir="/tmp"):
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

        self.CMDs = ["play", "pause", "next", "stop", "quit"]

        self.music_dir = music_dir
        if not os.path.exists(music_dir):
            print(f"Unable to find music directory {music_dir}")

        self.ws = connect(f"ws://localhost:{config.PORT}")

    def download_and_queue(self, url):
        download_opts = self.download_opts
        print(download_opts["outtmp"])

        with yt_dlp.YoutubeDL(download_opts) as audio:
            info_dict = audio.extract_info(url, download=True)

            title = info_dict["title"]
            format = "wav"  # hardcoded for now
            file = f"{audio.prepare_filename(info_dict).split(".")[0]}.{
                format}"
            song = {"title": title, "file": file, "format": format}
            self.queue(song)
            self.remove(song)

    def remove(self, song):
        print(f"Trying to remove {song["file"]}")
        try:
            os.remove(song["file"])
        except:
            print("Unable to remove file.")

    def command(self, cmd):
        cmd = cmd.lower()
        if cmd not in self.CMDs:
            print("Invalid command.")
            return

        try:
            self.ws.send(cmd)
        except:
            print(f"Unable to send {cmd} command.")

    def send_file(self, file):
        with open(file, "rb") as f:
            data = f.read(FILE_CHUNK)
            while (data):
                self.ws.send(data)
                data = f.read(FILE_CHUNK)
            self.ws.send("finished")

    def queue(self, song):
        try:
            self.ws.send("queue")
            self.ws.send(json.dumps(song))
            self.send_file(song["file"])
        except:
            print("Unable to send song information.")


def handler():
    host = Host()
    while True:
        command = input("Please input a command:")
        if command == "download":
            url = input("Please input the download url:")
            host.download_and_queue(url)

        elif command == "quit":
            break

        else:
            host.command(command)


if __name__ == "__main__":
    handler()
