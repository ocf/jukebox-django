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


async def send_time_packet(ws, controller):
    active = controller.get_active()

    if (not active):
        await send_packet(ws, "time", {"duration": 1, "curr_pos": 0})
        return

    duration = controller.get_duration()
    curr_pos = controller.get_curr_pos()
    await send_packet(ws, "time", {"duration": duration, "curr_pos": curr_pos})

async def send_lyric_packet(ws, controller):
    lyrics = controller.get_lyrics()
    await send_packet(ws, "lyrics", lyrics)


async def send_nowplaying_packet(ws, controller):
    active = controller.get_active()

    if not active or len(controller.song_list) == 0:
        await send_packet(ws, "now_playing", {"title": "Nothing Playing", "author": "No Author", "thumbnail": ""})
        return

    song = controller.song_list[0]
    await send_packet(ws, "now_playing", {"title": song.title, "author": song.author, "thumbnail": song.thumbnail})

async def send_queue_packet(ws, controller):
    songs = []
    for song in controller.song_list:
        songs.append({"title": song.title, "author": song.author,
                        "thumbnail": song.thumbnail})
    await send_packet(ws, "songs", {"songs": songs})
        

# Sends websocket packets to web interface


async def producer(ws, controller):
    while True:
        # Now playing song
        await send_nowplaying_packet(ws, controller)

        # Queued songs
        await send_queue_packet(ws, controller)

        # Current play time information
        await send_time_packet(ws, controller)

        # Lyrics
        await send_lyric_packet(ws, controller)
        
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
        
        elif packet_type == "time":
            new_pos = payload.get("new_pos")
            if new_pos == None:
                continue
            duration = controller.get_duration()
            controller.set_curr_pos(duration * new_pos)
            await send_time_packet(ws, controller)


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
