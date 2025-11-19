from piper.voice import PiperVoice
from pathlib import Path
import wave
import io

class TTSService:
    def __init__(self):
        model_path = Path(__file__).resolve().parent.parent / "model" / "en_US-lessac-medium.onnx"
        self.voice = PiperVoice.load(str(model_path))

    def synthesize(self, text: str) -> bytes:
        audio_iter = self.voice.synthesize(text)
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) 
            wf.setframerate(self.voice.config.sample_rate)

            if isinstance(audio_iter, (bytes, bytearray)):
                wf.writeframes(audio_iter)
            else:
                for chunk in audio_iter:
                    wf.writeframes(chunk.audio_int16_bytes)

        return buffer.getvalue()

tts_service = TTSService()
