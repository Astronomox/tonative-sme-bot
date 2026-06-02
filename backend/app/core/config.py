import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # PostgreSQL (raw connection)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Tonative
    TONATIVE_API_KEY: str = os.getenv("TONATIVE_API_KEY", "")
    TONATIVE_API_URL: str = os.getenv("TONATIVE_API_URL", "")

    # ElevenLabs
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def tonative_enabled(self) -> bool:
        return bool(self.TONATIVE_API_KEY and self.TONATIVE_API_URL)

    @property
    def elevenlabs_enabled(self) -> bool:
        return bool(self.ELEVENLABS_API_KEY)

    @property
    def groq_enabled(self) -> bool:
        return bool(self.GROQ_API_KEY)

    @property
    def supabase_enabled(self) -> bool:
        # kept for backward compat but unused
        return False


settings = Settings()
