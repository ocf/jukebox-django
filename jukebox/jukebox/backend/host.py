import config
import asyncio
import websockets
import aioconsole
from websockets.sync.client import connect

FILE_CHUNK = 1024
CMD = ["play", "pause", "next", "stop"]


async def consumer(message):
    print(f"Received {message}")


async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)


async def producer():
    command = await aioconsole.ainput(
        f"Please input a command (play, pause, next, stop, or quit): ")
    return command


async def producer_handler(websocket):
    while True:
        message = await producer()
        if message:
            await websocket.send(message)


async def handler(uri):
    async with websockets.connect(uri, ping_interval=10, ping_timeout=20) as websocket:
        consumer_task = asyncio.create_task(consumer_handler(websocket))
        producer_task = asyncio.create_task(producer_handler(websocket))

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

if __name__ == "__main__":
    uri = f"ws://localhost:{config.PORT}"
    asyncio.run(handler(uri))