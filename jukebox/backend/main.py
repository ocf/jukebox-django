import asyncio
from runner import Controller
import json
import config
import asyncio
from websockets.asyncio.server import serve

controller = Controller(music_dir="music")
async def send_packet(ws, type, payload={}):
    packet = json.dumps({"type": type, "payload": payload})
    await ws.send(packet)

# Sends websocket packets to web interface
async def producer(ws, controller):
    while True:
        # Now playing song
        if len(controller.song_list) >= 1:
            song = controller.song_list[0]
            await send_packet(ws, "now_playing", {"title": song.title, "author": song.author, "thumbnail": song.thumbnail})
        else:
            await send_packet(ws, "now_playing", {"title": "Nothing Playing", "author": "No Author", "thumbnail": ""})

        # Queued songs
        songs = []
        for song in controller.song_list:
            songs.append({"title": song.title, "author": song.author,
                        "thumbnail": song.thumbnail})
        await send_packet(ws, "songs", {"songs": songs})
        await asyncio.sleep(1)


# Receives websocket packets to web interface
async def consumer(ws, controller):
    async for message in ws:
        packet = json.loads(message)
        packet_type = packet.get("type")
        payload = packet.get("payload", {})

        if packet_type == "play":
            url = payload.get("url")
            controller.play(url)

        elif packet_type == "pause":
            controller.pause()
            if controller.is_paused():
                await send_packet(ws, "play_pause", {"status": "pause"})
            else:
                await send_packet(ws, "play_pause", {"status": "play"})

        elif packet_type == "next":
            controller.next()

        elif packet_type == "stop":
            controller.stop()

        elif packet_type == "quit":
            controller.quit()
            break
        
        elif packet_type == "volume":
            volume = payload.get("volume")
            if volume == None:
                continue
            controller.set_volume(volume)
            await send_packet(ws, "volume", {"volume": controller.get_volume()})

async def handler(ws):
    global controller

    producer_task = asyncio.create_task(producer(ws, controller))
    consumer_task = asyncio.create_task(consumer(ws, controller))
    try:
        await asyncio.gather(producer_task, consumer_task)
    finally:
        producer_task.cancel()
        consumer_task.cancel()


async def main():
    print(f"Starting server on port {config.PORT}")
    async with serve(handler, "", config.PORT, ping_interval=10, ping_timeout=20):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
