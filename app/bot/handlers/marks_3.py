import functools as ft
import re
import pyrogram
from pyrogram import Client, types
from app.bot import CallbackQuery
from app.dependencies import types as types_l, Postgresql


async def init(client: Client, cbQuery: CallbackQuery, db: Postgresql):
    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^marks_page$")))
    async def _marks_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_marks_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"(?i).*marks")))
    async def _marks(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        sender_id = str(sender.id)
        send_marks = ft.partial(
            cbQuery.send_marks,
            event=callback_query
        )
        match callback_query.data:
            case "all_marks":
                await send_marks(specific=types_l.MarkTypes.ALL)
            case "summative_marks":
                await send_marks(specific=types_l.MarkTypes.SUMMATIVE)
            case "final_marks":
                await send_marks(specific=types_l.MarkTypes.FINAL)
            case "recent_marks":
                await send_marks(specific=types_l.MarkTypes.RECENT)
        await db.increase_marks_counter(sender_id=sender_id)
        raise pyrogram.StopPropagation
