from piper.voice import PiperVoice
from pathlib import Path

model_path = Path(__file__).parent / "en_US-lessac-medium.onnx"
voice = PiperVoice.load(str(model_path))

audio_iter = voice.synthesize("test message")

for chunk in audio_iter:
    print("Chunk TYPE:", type(chunk))
    print("Chunk DIR:", dir(chunk))
    break