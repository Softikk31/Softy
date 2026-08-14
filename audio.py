import warnings

from config import language, model_id, device, speaker, sample_rate

warnings.filterwarnings('ignore', category=UserWarning)

import time
import torch
import sounddevice as sd

def audio_run(message: str):
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)

    audio = model.apply_tts(text=message,
                            speaker=speaker,
                            sample_rate=sample_rate)
    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop()