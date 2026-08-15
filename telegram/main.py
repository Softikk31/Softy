from dataclasses import dataclass
from datetime import datetime

from telethon import TelegramClient

from config import TG_API_KEY, TG_API_HASH


async def get_me():
    async with TelegramClient('softy', TG_API_KEY, TG_API_HASH) as client:
        return await client.get_me()

@dataclass
class DialogInfo:
    id: int
    name: str
    username: str | None

    pinned: bool
    unread_count: int

    last_message_id: int | None
    last_message: str | None
    last_message_date: datetime | None
    last_message_out: bool | None

    is_self: bool
    is_bot: bool
    is_verified: bool

async def get_dialogs():
    """
    Получить список всех Telegram-диалогов текущего аккаунта.

    Используй эту функцию, когда нужно:
    - узнать, с кем пользователь переписывается;
    - найти Telegram-диалог по имени или username;
    - получить ID нужного пользователя/чата перед отправкой сообщения;
    - узнать последнее сообщение в диалоге;
    - определить количество непрочитанных сообщений;
    - определить, является ли собеседник ботом, самим пользователем или верифицированным аккаунтом.

    Возвращает список объектов DialogInfo.

    Каждый DialogInfo содержит:
    - id: уникальный Telegram ID пользователя или чата;
    - name: отображаемое имя диалога;
    - username: username Telegram без символа @, если он существует;
    - pinned: закреплён ли диалог;
    - unread_count: количество непрочитанных сообщений;
    - last_message_id: ID последнего сообщения;
    - last_message: текст последнего сообщения;
    - last_message_date: дата и время последнего сообщения;
    - last_message_out: True, если последнее сообщение отправил текущий пользователь;
    - is_self: True, если диалог является чатом пользователя с самим собой;
    - is_bot: True, если собеседник является Telegram-ботом;
    - is_verified: True, если Telegram-аккаунт верифицирован.

    Важно:
    Если нужно отправить сообщение конкретному человеку, сначала используй
    эту функцию, чтобы найти нужный диалог и его Telegram ID.
    Не угадывай Telegram ID пользователя.
    """
    print('get_dialogs')
    async with TelegramClient('softy', TG_API_KEY, TG_API_HASH) as client:
        dialogs = []
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            message = dialog.message

            dialogs.append(
                DialogInfo(
                    id=dialog.id,
                    name=dialog.name,
                    username=getattr(entity, "username", None),

                    pinned=dialog.pinned,
                    unread_count=dialog.unread_count,

                    last_message_id=(
                        message.id
                        if message
                        else None
                    ),

                    last_message=(
                        message.message
                        if message
                        else None
                    ),

                    last_message_date=(
                        message.date
                        if message
                        else None
                    ),

                    last_message_out=(
                        message.out
                        if message
                        else None
                    ),

                    is_self=getattr(
                        entity,
                        "is_self",
                        False
                    ),

                    is_bot=getattr(
                        entity,
                        "bot",
                        False
                    ),

                    is_verified=getattr(
                        entity,
                        "verified",
                        False
                    ),
                )
            )
        return dialogs

async def send_message(user_id: int, message: str):
    """
    Отправить сообщение в Telegram указанному пользователю или чату.

    Используй эту функцию, когда пользователь явно просит:
    - отправить сообщение в Telegram;
    - написать человеку в Telegram;
    - отправить текст в определённый Telegram-чат.

    Параметры:
    user_id:
        Telegram ID пользователя или чата, которому нужно отправить сообщение.
        Если ID неизвестен, сначала используй get_dialogs(), чтобы найти
        нужный диалог.

    message:
        Точный текст сообщения, который необходимо отправить.

    Важно:
    - Не придумывай user_id.
    - Если пользователь указал имя или username, но Telegram ID неизвестен,
      сначала используй get_dialogs().
    - Перед отправкой убедись, что выбран правильный диалог.
    - Эта функция непосредственно отправляет сообщение и производит реальное
      действие в Telegram.
    """
    print('send_message')
    async with TelegramClient('softy', TG_API_KEY, TG_API_HASH) as client:
        await client.send_message(user_id, message)

