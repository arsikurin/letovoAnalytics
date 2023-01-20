import datetime
import functools as ft
import re

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import Postgresql, types as types_l
from config import settings


async def init(clients: types_l.clients[Client], cbQuery: CallbackQuery, db: Postgresql):
    client = clients.client

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^homework_page$")))
    async def _homework_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_homework_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^specific_day_homework$")))
    async def _specific_day_homework(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_specific_day_homework_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"(?i).*homework")))
    async def _homework(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        sender_id = str(sender.id)
        send_homework = ft.partial(
            cbQuery.send_homework,
            event=callback_query
        )

        match callback_query.data:
            case "tomorrows_homework":
                specific_day = types_l.Weekdays(int(datetime.datetime.now(tz=settings().timezone).strftime("%w")) + 1)

                await send_homework(
                    specific_day=specific_day if specific_day != types_l.Weekdays.SundayHW else types_l.Weekdays.Sunday
                )
            case "entire_homework":
                await send_homework(specific_day=types_l.Weekdays.Week)
            case "monday_homework":
                await send_homework(specific_day=types_l.Weekdays.Monday)
            case "tuesday_homework":
                await send_homework(specific_day=types_l.Weekdays.Tuesday)
            case "wednesday_homework":
                await send_homework(specific_day=types_l.Weekdays.Wednesday)
            case "thursday_homework":
                await send_homework(specific_day=types_l.Weekdays.Thursday)
            case "friday_homework":
                await send_homework(specific_day=types_l.Weekdays.Friday)
            case "saturday_homework":
                await send_homework(specific_day=types_l.Weekdays.Saturday)

        await db.increase_homework_counter(sender_id=sender_id)

        raise pyrogram.StopPropagation
