import asyncio
from asyncio import create_task
from datetime import datetime

from colorama import init, Fore
from ollama import Message

from audio import audio_run
from config import MY_TIME_ZONE, AUTHOR, LLM_MODEL, client, LOGO
from data.database import Database
from data.entities import MessageEntity, ChatEventEntity
from mappers import message_entity_to_ollama_message, memory_entities_to_json_memory
from memory_llm import memory_llm
from voice import voice_init

init(autoreset=True)

with open('resources/main_llm_prompt.txt', 'r') as file:
    prompt = file.read()


def datetime_converter(value: int) -> str:
    return '0' + str(value) if (value < 10) else str(value)


def startup():
    now = datetime.now(MY_TIME_ZONE)
    print(Fore.MAGENTA + LOGO)
    print(f'''
{Fore.BLUE + 'Author'}: {Fore.RESET + AUTHOR} 
{Fore.BLUE + 'Started'}: {Fore.RESET + datetime_converter(now.hour)}:{datetime_converter(now.minute)} {datetime_converter(now.day)}.{datetime_converter(now.month)}.{datetime_converter(now.year)}
    ''')


async def main():
    startup()
    database = Database()
    message_entity = MessageEntity()
    chat_event_entity = ChatEventEntity()
    await database.init_db()

    while True:
        message = voice_init()
        await message_entity.new_message('user', message)

        messages_result = message_entity_to_ollama_message(await message_entity.get_latest_messages())
        asyncio.create_task(memory_llm(messages_result))

        print('Output: ')
        output_ai = list()

        memory = await chat_event_entity.get_latest_memory()
        memory_text = memory_entities_to_json_memory(memory)

        messages = [
            Message(
                role="system",
                content=f"""
## PROMPT

{prompt}

## MEMORY

{memory_text}
"""
            ),
            *messages_result
        ]
        for chunk in client.chat(LLM_MODEL, messages=messages, think=False, stream=True):
            content = chunk['message']['content']
            print(Fore.MAGENTA + content + Fore.RESET, end='', flush=True)
            output_ai.append(content)
        message = ''.join(output_ai)
        if message != '':
            audio_run(message)
        create_task(message_entity.new_message('assistant', message))
        print()


try:
    if __name__ == "__main__":
        asyncio.run(main())
except Exception as _:
    pass
