from datetime import datetime

from ollama import Message
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import LLM_MODEL, MY_TIME_ZONE, engine, client
from database import ChatEventEntity


class ChatEventCreate(BaseModel):
    type: str
    importance: float
    content: str


class ChatEventResponse(BaseModel):
    events: list[ChatEventCreate]


def get_memory_llm_prompt() -> str:
    with open('resources/memory_llm_prompt.txt', 'r') as file:
        memory_llm_prompt = file.read()
    return memory_llm_prompt


async def memory_llm(messages: list[Message]):
    with Session(engine) as session:
        _messages = list(
            map(
                lambda _message: str({
                    'role': _message.role,
                    'content': _message.content
                }),
                messages
            )
        )

        memory_result = select(ChatEventEntity)

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

        response = client.chat(model=LLM_MODEL, messages=[
            {
                'role': 'system',
                'content': get_memory_llm_prompt(),
            },
            {
                'role': 'user',
                'content': f'''
Существующая память:
{memory_text}
Новые сообщения:
{''.join(_messages)}
    '''
            }
        ], think=False, format=ChatEventResponse.model_json_schema())
        events = ChatEventResponse.model_validate_json(response['message']['content']).events

        chat_events = list(
            map(
                lambda _event: ChatEventEntity(
                    created_at=datetime.now(MY_TIME_ZONE),
                    type=_event.type,
                    importance=_event.importance,
                    content=_event.content
                ),
                events
            )
        )

        for event in chat_events:
            session.add(event)
            session.commit()
