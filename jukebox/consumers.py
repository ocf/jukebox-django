import asyncio
from dataclasses import asdict
import json
import jsonpickle
from channels.generic.websocket import AsyncWebsocketConsumer

from jukebox.types.state import JukeboxState
from jukebox.types.time import TimeState
from .controller import get_controller
from django.conf import settings


class JukeboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = settings.ROOM_NAME
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        self.controller = get_controller()
        self.producer_task = asyncio.create_task(self.producer())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
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
            elif packet_type == "next":
                self.controller.next()
            elif packet_type == "stop":
                self.controller.stop()
            elif packet_type == "volume":
                volume = payload.get("volume")
                if volume is not None:
                    self.controller.set_volume(volume)
            elif packet_type == "time":
                new_pos = payload.get("new_pos")
                if new_pos is not None:
                    duration = self.controller.get_duration()
                    self.controller.set_curr_pos(duration * new_pos)

            state = await self.get_state()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "receive_broadcast",
                    "payload": asdict(state)
                }
            )

        except Exception as e:
            print("Error processing message:", e)
            pass

    async def producer(self):
        # Periodically sends jukebox state to the client
        try:
            while True:
                current_state = await self.get_state()
                await self.send_packet("now_playing", current_state.now_playing or {})
                await self.send_packet("songs", {"songs": current_state.queue})
                await self.send_packet("play_pause", {"status": current_state.status})
                await self.send_packet("volume", {"volume": current_state.volume})
                await self.send_packet("time", current_state.time)
                await self.send_packet("lyrics", current_state.lyrics)
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Producer error: {e}")
            pass

    async def get_state(self):
        # Gets current jukebox state from the controller
        active = self.controller.is_active()
        time_state = TimeState(
            duration=self.controller.get_duration() if active else 1,
            curr_pos=self.controller.get_curr_pos() if active else 0
        )
        return JukeboxState(
            volume=self.controller.get_volume(),
            status=self.controller.get_status(),
            time=time_state,
            now_playing=self.controller.get_first_song(),
            queue=self.controller.get_queue(),
            lyrics=self.controller.get_lyrics()
        )

    async def send_packet(self, packet_type, payload):
        await self.send(text_data=jsonpickle.encode({
            "type": packet_type,
            "payload": payload
        }, unpicklable=False))

    async def receive_broadcast(self, event):
        # Receives state updates from the controller and sends to the client
        try:
            payload = event.get("payload", {})
            await self.send_packet("now_playing", payload.get("now_playing") or {})
            await self.send_packet("songs", {"songs": payload.get("queue", [])})
            await self.send_packet("play_pause", {"status": payload.get("status")})
            await self.send_packet("volume", {"volume": payload.get("volume")})
            await self.send_packet("time", payload.get("time", {}))
            await self.send_packet("lyrics", payload.get("lyrics"))
        except Exception as e:
            print("Error sending broadcast state:", e)
            pass