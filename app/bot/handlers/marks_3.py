import functools as ft

from telethon import events, types, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import types as types_l, Postgresql


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: Postgresql):
    @client.on(events.CallbackQuery(data=b"marks_page"))
    async def _marks_page(event: events.CallbackQuery.Event):
        await cbQuery.to_marks_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(pattern=r"(?i).*marks"))
    async def _marks(event: events.CallbackQuery.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)
        send_marks = ft.partial(
            cbQuery.send_marks,
            event=event
        )
        match event.data:
            case b"all_marks":
                await send_marks(specific=types_l.MarkTypes.ALL)
            case b"summative_marks":
                await send_marks(specific=types_l.MarkTypes.SUMMATIVE)
            case b"final_marks":
                await send_marks(specific=types_l.MarkTypes.FINAL)
            case b"recent_marks":
                await send_marks(specific=types_l.MarkTypes.RECENT)
        await db.increase_marks_counter(sender_id=sender_id)
        raise events.StopPropagation
