import asyncio
from asyncio import create_task
from datetime import datetime

from colorama import init, Fore
from ollama import Message
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from audio import audio_run
from config import MY_TIME_ZONE, AUTHOR, LLM_MODEL, engine, client, LOGO
from database import MessageEntity, init_db, ChatEventEntity
from memory_llm import memory_llm
from voice import voice_init

init(autoreset=True)

with open('resources/main_llm_prompt.txt', 'r') as file:
    prompt = file.read()


async def new_message(session, role: str, message_text: str):
    session.add(MessageEntity(
        created_at=datetime.now(MY_TIME_ZONE),
        role=role,
        content=message_text
    ))
    session.commit()


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
    await init_db()
    with Session(engine) as session:
        while True:
            message = voice_init()
            await new_message(session, 'user', message)

            messages_query = select(MessageEntity).order_by(desc(MessageEntity.created_at)).limit(5)
            messages_result = reversed(session.scalars(
                messages_query
            ).all())

            _messages = list(map(
                lambda _message: Message(
                    role=_message.role,
                    content=_message.content
                ),
                messages_result
            ))

            asyncio.create_task(memory_llm(_messages))

            print('Output: ')
            output_ai = list()

            memory_result = select(ChatEventEntity).order_by(desc(ChatEventEntity.importance),
                                                             desc(ChatEventEntity.created_at)).limit(15)

            memory = session.scalars(memory_result).all()
            memory_text: list[str] = list(map(
                lambda _chat_event:
                str({
                    'id': _chat_event.id,
                    'created_at': _chat_event.created_at,
                    'type': _chat_event.type,
                    'importance': _chat_event.importance,
                    'content': _chat_event.content
                }),
                memory
            ))

            messages = [
                Message(
                    role="system",
                    content=f"""
{prompt}

## MEMORY

{memory_text}
"""
                ),
                *_messages
            ]
            for chunk in client.chat(LLM_MODEL, messages=messages, think=False, stream=True):
                content = chunk['message']['content']
                print(Fore.MAGENTA + content + Fore.RESET, end='', flush=True)
                output_ai.append(content)
            message = ''.join(output_ai)
            if message != '':
                audio_run(message)
            create_task(new_message(session, 'assistant', message))
            print()


try:
    if __name__ == "__main__":
        asyncio.run(main())
except Exception as _:
    pass
