from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.agent_service import agent_service
from app.services.tts_service import tts_service
import io
from fastapi import UploadFile, File, Form
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.services.stt_service import stt_service

router = APIRouter()

# @router.get("/ask")
# async def ask(question: str):
#     # Step 1 — generate text
#     answer = agent_service.ask(question)

#     # Step 2 — TTS audio
#     audio_bytes = tts_service.synthesize(answer)

#     return StreamingResponse(
#         io.BytesIO(audio_bytes),
#         media_type="audio/wav"
#     )


# @router.post("/ask")
# async def ask_audio(audio: UploadFile = File(...), mime_type: str = Form(None)):
#     # Step 0 — STT: transcribe incoming audio to text
#     data = await audio.read()
#     mt = mime_type or (audio.content_type or "audio/webm")
#     question = stt_service.transcribe_bytes(data, mt)

#     # Step 1 — generate text from agent using the transcribed question
#     answer = agent_service.ask(question)

#     # Step 2 — TTS audio for the agent's answer
#     audio_bytes = tts_service.synthesize(answer)

#     return StreamingResponse(
#         io.BytesIO(audio_bytes),
#         media_type="audio/wav"
#     )


# @router.post("/transcribe")
# async def transcribe(audio: UploadFile = File(...), mime_type: str = Form(None)):
#     data = await audio.read()
#     mt = mime_type or (audio.content_type or "audio/webm")
#     text = stt_service.transcribe_bytes(data, mt)
#     return JSONResponse({"text": text})


# @router.websocket("/ws/transcribe")
# async def ws_transcribe(ws: WebSocket):
#     await ws.accept()
#     buffer = bytearray()
#     mime_type: str = "audio/webm"
#     try:
#         while True:
#             message = await ws.receive()
#             if "bytes" in message and message["bytes"] is not None:
#                 buffer.extend(message["bytes"]) 
#             elif "text" in message and message["text"] is not None:
#                 payload = message["text"].strip().lower()
#                 if payload.startswith("mime:"):
#                     mime_type = payload.split(":", 1)[1].strip() or mime_type
#                     await ws.send_text("ok")
#                 elif payload == "flush":
#                     text = stt_service.transcribe_bytes(bytes(buffer), mime_type)
#                     await ws.send_text(text)
#                     buffer.clear()
#                 elif payload == "end":
#                     text = stt_service.transcribe_bytes(bytes(buffer), mime_type)
#                     await ws.send_text(text)
#                     await ws.close()
#                     break
#                 else:
#                     await ws.send_text("unknown")
#     except WebSocketDisconnect:
#         pass


@router.websocket("/ws/ask")
async def ws_ask(ws: WebSocket):
    await ws.accept()
    buffer = bytearray()
    mime_type: str = "audio/webm"
    try:
        while True:
            message = await ws.receive()
            if "bytes" in message and message["bytes"] is not None:
                buffer.extend(message["bytes"])  
            elif "text" in message and message["text"] is not None:
                payload = message["text"].strip().lower()
                if payload.startswith("mime:"):
                    mime_type = payload.split(":", 1)[1].strip() or mime_type
                    await ws.send_text("ok")
                elif payload == "end":
                    # Guard: no audio received
                    if not buffer:
                        await ws.send_text("no-audio")
                        await ws.close()
                        break

                    # 1) STT
                    question = stt_service.transcribe_bytes(bytes(buffer), mime_type)

                    # Guard: empty transcription
                    if not question or not question.strip():
                        await ws.send_text("no-transcript")
                        await ws.close()
                        break

                    # 2) Agent
                    answer = agent_service.ask(question)
                    # 3) TTS
                    audio_bytes = tts_service.synthesize(answer)
                    # Send WAV bytes back to client
                    await ws.send_bytes(audio_bytes)
                    await ws.close()
                    break
                else:
                    await ws.send_text("unknown")
    except WebSocketDisconnect:
        pass
