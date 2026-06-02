from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.conversation import handle_incoming_message

router = APIRouter(prefix="/test", tags=["test"])


class TestMessage(BaseModel):
    phone_number: str = "whatsapp:+2341234567890"
    message: str = ""
    is_voice: bool = False


@router.post("/chat")
async def test_chat(msg: TestMessage):
    """
    Test the bot locally without Twilio.
    Send a JSON body like:
    {
        "phone_number": "whatsapp:+2341234567890",
        "message": "Hello, I sell food in Lagos"
    }
    """
    result = await handle_incoming_message(
        phone_number=msg.phone_number,
        body=msg.message,
        media_url=None,
        num_media=0,
    )

    return {
        "user_message": msg.message,
        "bot_response": result["text_response"],
        "has_audio": result.get("audio_bytes") is not None,
    }
