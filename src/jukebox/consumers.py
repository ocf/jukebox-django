import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .controller import get_controller


class JukeboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.controller = get_controller()
        self.producer_task = asyncio.create_task(self.producer())

    async def disconnect(self, close_code):
        if hasattr(self, 'producer_task'):
            self.producer_task.cancel()

    async def receive(self, text_data):
        try:
            packet = json.loads(text_data)
            packet_type = packet.get("type")
            payload = packet.get("payload", {})

            if packet_type == "play":
                url = payload.get("url")
                if url:
                    self.controller.play(url)

            elif packet_type == "pause":
                self.controller.pause()
                status = "pause" if self.controller.is_paused() else "play"
                await self.send_packet("play_pause", {"status": status})

            elif packet_type == "next":
                self.controller.next()

            elif packet_type == "stop":
                self.controller.stop()

            elif packet_type == "volume":
                volume = payload.get("volume")
                if volume is not None:
                    self.controller.set_volume(volume)
                    await self.send_packet("volume", {"volume": self.controller.get_volume()})

            elif packet_type == "time":
                new_pos = payload.get("new_pos")
                if new_pos is not None:
                    duration = self.controller.get_duration()
                    self.controller.set_curr_pos(duration * new_pos)
                    await self.send_time_packet()

        except json.JSONDecodeError:
            pass

    async def send_packet(self, type, payload=None):
        if payload is None:
            payload = {}
        await self.send(text_data=json.dumps({"type": type, "payload": payload}))

    async def send_time_packet(self):
        active = self.controller.get_active()
        if not active:
            await self.send_packet("time", {"duration": 1, "curr_pos": 0})
            return

        duration = self.controller.get_duration()
        curr_pos = self.controller.get_curr_pos()
        await self.send_packet("time", {"duration": duration, "curr_pos": curr_pos})

    async def send_nowplaying_packet(self):
        active = self.controller.get_active()
        if not active or len(self.controller.song_list) == 0:
            await self.send_packet("now_playing", {
                "title": "Nothing Playing",
                "author": "No Author",
                "thumbnail": ""
            })
            return

        song = self.controller.song_list[0]
        await self.send_packet("now_playing", {
            "title": song.title,
            "author": song.author,
            "thumbnail": song.thumbnail
        })

    async def send_queue_packet(self):
        songs = []
        for song in self.controller.song_list:
            songs.append({
                "title": song.title,
                "author": song.author,
                "thumbnail": song.thumbnail
            })
        await self.send_packet("songs", {"songs": songs})

    async def send_lyric_packet(self):
        lyrics = self.controller.get_lyrics()
        await self.send_packet("lyrics", lyrics)

    async def producer(self):
        """Send state updates to client every second."""
        try:
            while True:
                await self.send_nowplaying_packet()
                await self.send_queue_packet()
                await self.send_time_packet()
                await self.send_lyric_packet()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
