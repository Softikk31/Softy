import os
from zoneinfo import ZoneInfo

import torch
from dotenv import load_dotenv
from ollama import Client
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

# Ollama
AUTHOR = 'Softikk'
MY_TIME_ZONE = ZoneInfo('Europe/Moscow')
LLM_MODEL = 'gemma4:cloud'
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')

if OLLAMA_API_KEY is None:
    raise ValueError('Api key is none')

client = Client(host='https://ollama.com',
                headers={'Authorization': 'Bearer ' + OLLAMA_API_KEY})

# Postgres
engine = create_async_engine('postgresql+asyncpg://postgres:311310d31$D@localhost/softy')
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

LOGO = '''
.▄▄ ·       ·▄▄▄▄▄▄▄▄ ▄· ▄▌
▐█ ▀. ▪     ▐▄▄·•██  ▐█▪██▌
▄▀▀▀█▄ ▄█▀▄ ██▪  ▐█.▪▐█▌▐█▪
▐█▄▪▐█▐█▌.▐▌██▌. ▐█▌· ▐█▀·.
 ▀▀▀▀  ▀█▄▀▪▀▀▀  ▀▀▀   ▀ • 
 '''

# Audio
language = 'ru'
model_id = 'v5_ru'
sample_rate = 48000
speaker = 'baya'
device = torch.device('cpu')

# Telegram
TG_API_KEY = os.environ.get('API_KEY')
TG_API_HASH = os.environ.get('API_HASH')
