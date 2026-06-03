import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    # Groq (LLM + Whisper fallback)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # AethexAI (TTS + Transcription primary)
    AETHEX_API_KEY: str = os.getenv("AETHEX_API_KEY", "")
    AETHEX_BASE_URL: str = "https://api.aethexai.com/api/v1"

    # PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Public URL for serving TTS audio back to WhatsApp
    PUBLIC_URL: str = os.getenv("PUBLIC_URL", "https://tonative-sme-bot.onrender.com")

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def aethex_enabled(self) -> bool:
        return bool(self.AETHEX_API_KEY)

    @property
    def groq_enabled(self) -> bool:
        return bool(self.GROQ_API_KEY)


settings = Settings()
