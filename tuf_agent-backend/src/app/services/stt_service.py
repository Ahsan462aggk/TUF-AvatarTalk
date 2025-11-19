from typing import Optional
import base64
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings


class STTService:
    def __init__(self) -> None:
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    def transcribe_bytes(self, audio_bytes: bytes, mime_type: str) -> str:
        if not audio_bytes:
            return ""
        encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Transcribe the audio."},
                {"type": "media", "data": encoded_audio, "mime_type": mime_type},
            ]
        )
        resp = self.llm.invoke([message])
        return resp.content if isinstance(resp.content, str) else str(resp.content)


stt_service = STTService()
