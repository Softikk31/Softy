from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import MY_TIME_ZONE, engine


class Base(DeclarativeBase):
    pass


class MessageEntity(Base):
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(name='id', primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(name='created_at',
                                                 default=lambda: datetime.now(MY_TIME_ZONE))
    role: Mapped[str] = mapped_column(name='role')
    content: Mapped[str] = mapped_column(name='content')


class ChatEventEntity(Base):
    __tablename__ = 'chat_event'

    id: Mapped[UUID] = mapped_column(name='id', primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(name='created_at',
                                                 default=lambda: datetime.now(MY_TIME_ZONE))
    type: Mapped[str] = mapped_column(name='type')
    importance: Mapped[float] = mapped_column('importance')
    content: Mapped[str] = mapped_column(name='content')

async def init_db():
    Base.metadata.create_all(bind=engine)
