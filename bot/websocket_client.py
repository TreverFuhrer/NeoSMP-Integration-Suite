import asyncio
import json
import websockets
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from event_handlers import chat_handler
#, whitelist_handler  # Import event handlers

load_dotenv()
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")

# Event dictionary: Maps events to handler functions
EVENTS = {
    "CHAT_MESSAGE": chat_handler.process_chat_message
    #"WHITELIST_REQUEST": whitelist_handler.process_whitelist_request
}

# Connect bot to plugin websocket server
async def connect_to_websocket():
    async with websockets.connect(
        WEBSOCKET_URL,
        extra_headers={"AUTH_TOKEN": AUTH_TOKEN}
    ) as websocket:
        print("Connected to the WebSocket server.")

        global plugin_connection
        plugin_connection = websocket
        
        try:
            # Handle plugin signal messages
            while True:
                handle_signals(websocket)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")


# Handle incoming signal message
async def handle_signals(websocket):
    signal = await websocket.recv()
    print(f"Received from Minecraft server: {signal}")
                
    # Parse the signal as JSON
    data = json.loads(signal)
    event_type = data.get("type")

    # Route the signal to the correct event handler
    handler = EVENTS.get(event_type)
    if handler:
        await handler(data)
    else:
        print(f"Unrecognized event type: {event_type}")


# Send signal message to plugin
async def send_signal(message_type, data):
    """Send a JSON message to the WebSocket server."""
    if plugin_connection:
        signal = {"type": message_type, **data}
        await plugin_connection.send(json.dumps(signal))
    else:
        print("WebSocket connection not established.")


# Start client
def start_websocket_client():
    asyncio.create_task(connect_to_websocket())