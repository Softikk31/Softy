import warnings

from config import language, model_id, device, speaker, sample_rate

warnings.filterwarnings('ignore', category=UserWarning)

import time
import torch
import sounddevice as sd
from transliterate import translit
from num2words import num2words

def transcriptor(message_param: str) -> str:
    message = message_param
    for word in (message.split(' ')):
        if any([char.isdigit() for char in word]):
            digits = ''
            for char in word:
                if char.isdigit():
                    digits += char
            new = num2words(int(digits), lang='ru')
            message = message.replace(word, new)
    return translit(message, 'ru')

def audio_run(message: str):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)

    audio = model.apply_tts(text=transcriptor(message),
                            speaker=speaker,
                            sample_rate=sample_rate)
    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop()