import sys
import json
from vosk import Model, KaldiRecognizer
import wave
import os

audio_file = sys.argv[1]
# Convert ogg to wav if needed
if audio_file.endswith('.ogg'):
    from pydub import AudioSegment
    sound = AudioSegment.from_ogg(audio_file)
    # Convert to mono, 16kHz, 16-bit PCM
    sound = sound.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    wav_file = audio_file.replace('.ogg', '.wav')
    sound.export(wav_file, format="wav")
    audio_file = wav_file

wf = wave.open(audio_file, "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 44100, 48000):
    print("Audio file must be WAV format mono PCM.")
    sys.exit(1)

model_path = "/root/.openclaw/workspace/models/vosk/vosk-model-small-ru-0.22"
model = Model(model_path)
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

results = []
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)

part_result = json.loads(rec.FinalResult())
results.append(part_result)

text = " ".join([res.get("text", "") for res in results if res.get("text")])
print(text.strip())

if 'wav_file' in locals():
    os.remove(wav_file)