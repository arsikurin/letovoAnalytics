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

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^schedule_page$")))
    async def _schedule_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_schedule_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^specific_day_schedule$")))
    async def _specific_day_schedule(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_specific_day_schedule_page(event=callback_query)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"(?i).*schedule$")))
    async def _schedule(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        sender_id = str(sender.id)
        send_schedule = ft.partial(
            cbQuery.send_schedule,
            event=callback_query
        )

        match callback_query.data:
            case "today_schedule":
                await send_schedule(specific_day=types_l.Weekdays(
                    int(datetime.datetime.now(tz=settings().timezone).strftime("%w"))
                ))
            case "entire_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Week)
            case "monday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Monday)
            case "tuesday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Tuesday)
            case "wednesday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Wednesday)
            case "thursday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Thursday)
            case "friday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Friday)
            case "saturday_schedule":
                await send_schedule(specific_day=types_l.Weekdays.Saturday)

        await db.increase_schedule_counter(sender_id=sender_id)

        raise pyrogram.StopPropagation
