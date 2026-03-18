import speech_recognition as sr
from pydub import AudioSegment
import sys
import os

audio_file = sys.argv[1]
# Convert ogg to wav
sound = AudioSegment.from_ogg(audio_file)
wav_file = audio_file.replace('.ogg', '.wav')
sound.export(wav_file, format="wav")

r = sr.Recognizer()
with sr.AudioFile(wav_file) as source:
    audio = r.record(source)
try:
    text = r.recognize_google(audio, language='ru-RU')
    print(text)
except sr.UnknownValueError:
    print("Не удалось распознать речь")
except sr.RequestError as e:
    print(f"Ошибка сервиса распознавания: {e}")
finally:
    os.remove(wav_file)