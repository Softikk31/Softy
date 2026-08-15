import asyncio
from asyncio import create_task
from datetime import datetime
from enum import Enum

from colorama import init, Fore
from ollama import Message

from audio import audio_run
from config import MY_TIME_ZONE, AUTHOR, LLM_MODEL, client, LOGO
from data.database import Database
from data.entities import MessageEntity, ChatEventEntity
from mappers import message_entity_to_ollama_message, memory_entities_to_json_memory
from memory_llm import memory_llm
from telegram.main import get_me, send_message, get_dialogs, DialogInfo
from voice import voice_init

init(autoreset=True)


class WorkMode(Enum):
    TEXT = 1
    VOICE = 2


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

    work_mode = int(input('''
Work mode:
1. Text
2. Voice

Input: '''))

    messages = []
    while True:
        message: str
        match work_mode:
            case WorkMode.TEXT.value:
                message = input('Input: ')
            case WorkMode.VOICE.value:
                message = voice_init()
            case _:
                message = input('Input: ')
        await message_entity.new_message('user', message)

        messages_entity = await message_entity.get_latest_messages()
        messages_result = message_entity_to_ollama_message(messages_entity)

        asyncio.create_task(memory_llm(messages_result))

        print('Output: ')
        output_ai = list()

        memory_entity = await chat_event_entity.get_latest_memory()
        memory_json = memory_entities_to_json_memory(reversed(memory_entity))

        messages.append(
            Message(
                role="system",
                content=f"""
    ## PROMPT
    {prompt}
    
    ## MEMORY
    {memory_json}
    
    ## INFO
    time: {datetime.now(MY_TIME_ZONE)}
    
    ## TELEGRAM INFO
    {await get_me()}
    
    """
            )
        )

        for message in reversed(messages_result):
            messages.append(message)

        while True:
            response = client.chat(LLM_MODEL, messages=messages, think=False, stream=True, tools=[get_dialogs, send_message])
            tool_called = False
            for chunk in response:
                content = chunk['message']['content']
                print(Fore.MAGENTA + content + Fore.RESET, end='', flush=True)
                output_ai.append(content)

                if chunk.message.tool_calls:
                    tool_called = True

                    messages.append(chunk.message)
                    for tool in chunk.message.tool_calls:
                        if tool.function.name == 'send_message':
                            args = tool.function.arguments
                            await send_message(**args)
                        if tool.function.name == 'get_dialogs':
                            dialogs: list[DialogInfo] = await get_dialogs()
                            messages.append(
                                Message(
                                    role="assistant",
                                    content=f'{dialogs}'
                                )
                            )

            message = ''.join(output_ai)
            if message != '':
                audio_run(message)
            create_task(message_entity.new_message('assistant', message))
            print()

            if not tool_called:
                break

# try:
if __name__ == "__main__":
    asyncio.run(main())
# except Exception as _:
#     pass
