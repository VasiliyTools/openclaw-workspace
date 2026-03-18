import sys
import piper

model_path = "/root/.openclaw/workspace/models/piper/ru_RU-irina-medium.onnx"
config_path = "/root/.openclaw/workspace/models/piper/ru_RU-irina-medium.onnx.json"

text = sys.argv[1] if len(sys.argv) > 1 else "Привет, это тест голосового синтеза."

voice = piper.PiperVoice.load(model_path, config_path=config_path)
with open("/tmp/output.wav", "wb") as wav_file:
    voice.synthesize(text, wav_file)

print("/tmp/output.wav")