import asyncio
from runner import Controller
import json
import config
import asyncio
import websockets
from websockets.asyncio.server import serve

controller = Controller(music_dir="music")

async def handler(ws):
    global controller
    async for message in ws:
        try:
            packet = json.loads(message)
            packet_type = packet.get("type")
            payload = packet.get("payload", {})
            
            if packet_type == "play":
                url = payload.get("url")
                controller.play(url)
            
            elif packet_type == "pause":
                controller.pause()
            
            elif packet_type == "next":
                controller.next()
            
            elif packet_type == "stop":
                controller.stop()
                
            elif packet_type == "quit":
                controller.quit()
                break
            
        except json.JSONDecodeError:
            print("Invalid packet received.")

    controller.song_queue.join()

async def main():
    print(f"Starting server on port {config.PORT}");
    async with serve(handler, "", config.PORT, ping_interval=10, ping_timeout=20):
        await asyncio.get_running_loop().create_future()
    
if __name__ == "__main__":
    asyncio.run(main())