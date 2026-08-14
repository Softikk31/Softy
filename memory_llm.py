from datetime import datetime

from ollama import Message
from pydantic import BaseModel

from config import LLM_MODEL, MY_TIME_ZONE, client
from data.entities import ChatEventEntity
from mappers import ollama_message_to_json_message, memory_entities_to_json_memory


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
    chat_event_entity = ChatEventEntity()

    memory = await chat_event_entity.get_all_memory()

    response = client.chat(model=LLM_MODEL, messages=[
        {
            'role': 'system',
            'content': get_memory_llm_prompt(),
        },
        {
            'role': 'user',
            'content': f'''
Существующая память:
{memory_entities_to_json_memory(memory)}
Новые сообщения:
{''.join(ollama_message_to_json_message(messages))}
'''
        }
    ], think=False, format=ChatEventResponse.model_json_schema())
    events = ChatEventResponse.model_validate_json(response['message']['content']).events

    for event in events:
        await chat_event_entity.new_memory(
            created_at=datetime.now(MY_TIME_ZONE),
            type_event=event.type,
            importance=event.importance,
            content=event.content
        )
