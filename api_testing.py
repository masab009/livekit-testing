from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext, WorkerOptions
from livekit.plugins import groq, elevenlabs, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

async def entrypoint(ctx: JobContext):
    await ctx.connect()

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

if __name__ == "__main__":
    agents.cli.run_app(WorkerOptions(entrypoint_func=entrypoint))