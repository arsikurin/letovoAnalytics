import asyncio
import datetime
import re
import time

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import run_sequence, run_parallel, types as types_l


async def init(clients: types_l.Clients[Client], cbQuery: CallbackQuery):
    client = clients.client

    @client.on_message(pyrogram.filters.user([606336225, 2200163963]) & pyrogram.filters.regex(re.compile(r"^#dev$")))
    async def _dev(_client: Client, message: types.Message):
        sender: types.User = message.from_user
        await run_sequence(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_dev_page(sender=sender)
        )
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.regex(re.compile(r"^#ping$")))
    @clients.client_i.on_message(pyrogram.filters.regex(re.compile(r"^#ping$")))
    async def _ping(_client: Client, message: types.Message):
        start_time = time.perf_counter()
        message_pong = await message.reply("Pong!")
        took = datetime.timedelta(seconds=time.perf_counter() - start_time)
        await run_parallel(
            message.delete(),
            run_sequence(
                message_pong.edit(f"Pong! __(reply took {took.total_seconds()}s)__"),
                asyncio.sleep(5),
                message_pong.delete()
            )
        )
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^stats$")))
    async def _stats(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        await run_sequence(
            cbQuery.send_stats(sender=sender),
            callback_query.answer("Has been sent")
        )
        raise pyrogram.StopPropagation

    @client.on_callback_query(
        pyrogram.filters.user([606336225, 2200163963]) & pyrogram.filters.regex(re.compile(r"^tokens$")))
    async def _tokens(_client: Client, callback_query: types.CallbackQuery):
        from app.helper import main
        await run_sequence(
            main(),
            callback_query.answer("Tokens updated in the Database")
        )
        raise pyrogram.StopPropagation
