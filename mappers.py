from ollama import Message


def message_entity_to_ollama_message(messages) -> list[Message]:
    return [Message(role=msg.role, content=msg.content) for msg in messages]


def ollama_message_to_json_message(messages) -> list[str]:
    return [str({'role': msg.role, 'content': msg.content}) for msg in messages]


def memory_entities_to_json_memory(memory) -> list[str]:
    return [str(
        {'id': event.id, 'created_at': event.created_at, 'type': event.type,
         'importance': event.importance, 'content': event.content}) for event in memory]
