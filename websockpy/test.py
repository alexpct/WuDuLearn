import asyncio
import websockets

async def websocket_server(websocket, path):
    while True:
        message = await websocket.recv()
        print(f"Nachricht empfangen: {message}")  # Zum Debuggen

        # Echo der empfangenen Nachricht
        await websocket.send(f"Echo: {message}")

start_server = websockets.serve(websocket_server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
