import os.path
import subprocess

import edge_tts


async def audio(message: str):
    communicate = edge_tts.Communicate(
        message,
        voice="ru-RU-SvetlanaNeural",
        pitch="+18Hz",
        rate="+15%"
    )

    file_path = '/tmp/voice.mp3'

    await communicate.save(file_path)
    subprocess.run(["mpg123", "-q", file_path])

    if os.path.exists(file_path):
        os.remove(file_path)
