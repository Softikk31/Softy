import speech_recognition
from speech_recognition import UnknownValueError

def voice_init() -> str:
    try:
        sr = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as mic:
            sr.adjust_for_ambient_noise(source=mic)
            audio = sr.listen(source=mic, timeout=None)
        return sr.recognize_google(audio_data=audio, language='ru-RU').lower()
    except UnknownValueError as _:
        return voice_init()
