import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from ollama import Client
from sqlalchemy import create_engine

load_dotenv()

AUTHOR = 'Softikk'
MY_TIME_ZONE = ZoneInfo('Europe/Moscow')
LLM_MODEL = 'gemma4:cloud'
API_KEY = os.environ.get('OLLAMA_API_KEY')

if API_KEY is None:
    raise ValueError('Api key is none')

engine = create_engine('postgresql+psycopg2://postgres:311310d31$D@localhost/softy')

client = Client(host='https://ollama.com',
                headers={'Authorization': 'Bearer ' + API_KEY})

LOGO = '''
.▄▄ ·       ·▄▄▄▄▄▄▄▄ ▄· ▄▌
▐█ ▀. ▪     ▐▄▄·•██  ▐█▪██▌
▄▀▀▀█▄ ▄█▀▄ ██▪  ▐█.▪▐█▌▐█▪
▐█▄▪▐█▐█▌.▐▌██▌. ▐█▌· ▐█▀·.
 ▀▀▀▀  ▀█▄▀▪▀▀▀  ▀▀▀   ▀ • 
 '''
