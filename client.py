import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from livekit import rtc

load_dotenv()

async def fetch_token():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/get-token",
                json={"room_name": "voice-assistant-room", "participant_identity": "test-client"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Token fetch failed: {await response.text()}")
                data = await response.json()
                return data["token"]
    except Exception as e:
        print(f"Error fetching token: {e}")
        raise

async def main():
    try:
        token = await fetch_token()
        room = rtc.Room()
        await room.connect(
            url="wss://jazz-sales-o2pqg79t.livekit.cloud",
            token=token
        )
        print("Connected to room:", room.name)

        # Listen for agent audio
        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print(f"Subscribed to audio from {participant.identity}")
                # Note: Server-side SDK doesn't support direct audio playback
                # For testing, log subscription; frontend handles playback

        # Stay connected
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())