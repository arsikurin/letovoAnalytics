import re

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import Postgresql, run_parallel, types as types_l


async def init(clients: types_l.clients[Client], cbQuery: CallbackQuery, db: Postgresql):
    client = clients.client

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^others_page$")))
    async def _others_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_others_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^teachers$")))
    async def _teachers(_client: Client, callback_query: types.CallbackQuery):
        await run_parallel(
            cbQuery.send_teachers(event=callback_query),
            # db.increase_teachers_counter(sender_id=sender_id)
        )
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^holidays$")))
    async def _holidays(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        sender_id = str(sender.id)
        await run_parallel(
            cbQuery.send_holidays(event=callback_query),
            db.increase_holidays_counter(sender_id=sender_id)
        )
        raise pyrogram.StopPropagation
