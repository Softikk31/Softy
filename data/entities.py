from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, desc, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import MY_TIME_ZONE, async_session_maker


class Base(DeclarativeBase):
    pass


class MessageEntity(Base):
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(name='id', primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), name='created_at',
                                                 default=lambda: datetime.now(MY_TIME_ZONE))
    role: Mapped[str] = mapped_column(name='role')
    content: Mapped[str] = mapped_column(name='content')

    @staticmethod
    async def new_message(role: str, message_text: str):
        async with async_session_maker() as session:
            async with session.begin():
                session.add(MessageEntity(
                    created_at=datetime.now(MY_TIME_ZONE),
                    role=role,
                    content=message_text
                ))

    @staticmethod
    async def get_latest_messages():
        async with async_session_maker() as session:
            messages_query = select(MessageEntity).order_by(desc(MessageEntity.created_at)).limit(5)
            messages_result = (await session.scalars(
                messages_query
            )).all()
            return list(messages_result)


class ChatEventEntity(Base):
    __tablename__ = 'chat_event'

    id: Mapped[UUID] = mapped_column(name='id', primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), name='created_at',
                                                 default=lambda: datetime.now(MY_TIME_ZONE))
    type: Mapped[str] = mapped_column(name='type')
    importance: Mapped[float] = mapped_column('importance')
    content: Mapped[str] = mapped_column(name='content')

    @staticmethod
    async def new_memory(created_at, type_event, importance, content):
        async with async_session_maker() as session:
            async with session.begin():
                session.add(ChatEventEntity(
                    created_at=created_at,
                    type=type_event,
                    importance=importance,
                    content=content
                ))

    @staticmethod
    async def get_all_memory():
        async with async_session_maker() as session:
            memory_result = select(ChatEventEntity)
            memory = (await session.scalars(memory_result)).all()
            return list(memory)

    @staticmethod
    async def get_latest_memory():
        async with async_session_maker() as session:
            memory_result = select(ChatEventEntity).order_by(desc(ChatEventEntity.importance),
                                                             desc(ChatEventEntity.created_at)).limit(15)

            return list((await session.scalars(memory_result)).all())
