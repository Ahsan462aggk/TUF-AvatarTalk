from piper.voice import PiperVoice
from pathlib import Path
import wave

model_path = Path(__file__).parent / "en_US-lessac-medium.onnx"
voice = PiperVoice.load(str(model_path))

text = "Hello! Piper TTS is fully working now."

audio_iter = voice.synthesize(text)

with wave.open("test.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit audio
    wf.setframerate(voice.config.sample_rate)

    # Case 1: model returns raw bytes (rare)
    if isinstance(audio_iter, (bytes, bytearray)):
        wf.writeframes(audio_iter)

    # Case 2: model returns AudioChunk (your case)
    else:
        for chunk in audio_iter:
            wf.writeframes(chunk.audio_int16_bytes)
