from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation import handle_incoming_message

router = APIRouter(prefix="/test", tags=["test"])


class TestMessage(BaseModel):
    phone_number: str = "whatsapp:+2341234567890"
    message: str = ""


@router.post("/chat")
async def test_chat(msg: TestMessage):
    """Test the bot locally without Twilio. POST {"message": "Hello"}"""
    result = await handle_incoming_message(
        phone_number=msg.phone_number,
        body=msg.message,
    )
    return {
        "user": msg.message,
        "bot": result["text_response"],
    }
