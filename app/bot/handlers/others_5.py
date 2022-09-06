import re

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import Postgresql, run_parallel


async def init(client: Client, cbQuery: CallbackQuery, db: Postgresql):
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

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^diploma$")))
    async def _diploma(_client: Client, callback_query: types.CallbackQuery):
        # await run_parallel(
        #     cbQuery.send_...(event=event),
        #     # db.increase_..._counter(sender_id=sender_id)
        # )
        await callback_query.answer("Not implemented!")
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
