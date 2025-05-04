import os
import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, WorkerOptions, WorkerPermissions, AutoSubscribe
from livekit.plugins import (
    noise_cancellation,
    silero,
    groq,
    elevenlabs
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

ROOM_NAME = "voice-assistant-room"
IDENTITY = "python-agent"

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

    async def on_llm_response(self, response: str, **kwargs) -> None:
        logging.info(f"LLM Response: {response}")
        await self.room.local_participant.publish_data(
            data={"event": "response", "data": {"text": response}},
            reliable=True
        )

    async def on_transcription(self, text: str, **kwargs) -> None:
        logging.info(f"Transcription: {text}")
        await self.room.local_participant.publish_data(
            data={"event": "transcribed_text", "data": {"text": text}},
            reliable=True
        )

async def entrypoint(ctx: agents.JobContext):
    logging.info("Starting entrypoint...")
    logging.info(f"Connecting to room: {ROOM_NAME} with identity: {IDENTITY}")
    logging.info(f"Connecting to room: {ROOM_NAME}")
    try:

        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        logging.info(f"Connected to room: {ctx.room.name}")
        logging.info(f"Local participant identity: {ctx.room.local_participant.identity}")
    except Exception as e:
        logging.error(f"Failed to connect: {e}")
        return

    try:
        session = AgentSession(
            stt=groq.STT(model="whisper-large-v3-turbo", language="ur"),
            llm=groq.LLM(model="llama-3.3-70b-versatile"),
            tts=elevenlabs.TTS(voice_id="Sxk6njaoa7XLsAFT7WcN", model="eleven_multilingual_v2"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )

        await session.start(
            room=ctx.room,
            agent=Assistant(),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )

        await session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )
    except Exception as e:
        logging.error(f"Session error: {e}")

if __name__ == "__main__":
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        permissions=WorkerPermissions(
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ),
    )
    agents.cli.run_app(opts)