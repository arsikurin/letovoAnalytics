#!/usr/bin/python3.9

# import re
import asyncio
import sqlite3
# import sys
# import datetime
# import time
import logging as log

from requests_futures.sessions import FuturesSession
from pprint import pprint
from datetime import date
from telethon import TelegramClient, events, errors
from essential import API_ID, API_HASH, BOT_TOKEN, init_user_sql, is_inited, is_inited_sql, \
    send_certain_day_schedule, send_greeting, send_main_page, send_holidays, send_init_message, \
    to_main_page, to_schedule_page, to_homework_page, to_certain_day_schedule_page, to_certain_day_homework_page, \
    receive_token, receive_student_id, get_message_sql, update_data, set_message_sql

"https://s-api.letovo.ru/api/students/54405"
"https://s-api.letovo.ru/api/studentsimg/54405"

client = TelegramClient("letovoAnalytics", API_ID, API_HASH)

with FuturesSession() as session:
    with sqlite3.Connection("users.sql") as connection:
        cursor = sqlite3.Cursor(connection)


    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def handle_start(event: events.NewMessage.Event):
        sender = await event.get_sender()
        chat_id = str(sender.id)
        _, ii = await asyncio.gather(send_greeting(client=client, sender=sender),
                                     is_inited(chat_id=chat_id))

        if not ii:
            await send_init_message(client=client, sender=sender)

            if not await is_inited_sql(chat_id=chat_id, conn=connection, c=cursor):
                await init_user_sql(chat_id=chat_id, conn=connection, c=cursor)
            raise events.StopPropagation

        # await send_main_page(client=client, sender=sender)
        # await set_message_sql(chat_id=chat_id, message_id=event.message.id + 3, conn=conn, c=c)
        await asyncio.gather(send_main_page(client=client, sender=sender),
                             update_data(chat_id=chat_id, token=await receive_token(session, chat_id)),
                             set_message_sql(chat_id=chat_id, message_id=event.message.id + 3, conn=connection, c=cursor))
        await update_data(chat_id=chat_id, student_id=await receive_student_id(session, chat_id)),


    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def schedule(event: events.CallbackQuery.Event):
        chat_id: str = str(event.original_update.user_id)
        if event.data == b"todays_schedule":
            await send_certain_day_schedule(specific_day=int(date.today().strftime("%w")) - 1,
                                            event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"entire_schedule":
            await send_certain_day_schedule(specific_day=-10, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"monday_schedule":
            await send_certain_day_schedule(specific_day=0, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"tuesday_schedule":
            await send_certain_day_schedule(specific_day=1, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"wednesday_schedule":
            await send_certain_day_schedule(specific_day=2, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"thursday_schedule":
            await send_certain_day_schedule(specific_day=3, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"friday_schedule":
            await send_certain_day_schedule(specific_day=4, event=event, client=client, s=session, chat_id=chat_id)

        elif event.data == b"saturday_schedule":
            await send_certain_day_schedule(specific_day=5, event=event, client=client, s=session, chat_id=chat_id)


    @client.on(events.CallbackQuery(pattern=r"(?i).*homework"))
    async def homework(event: events.CallbackQuery.Event):
        chat_id: str = str(event.original_update.user_id)
        if event.data == b"tomorrows_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(int(date.today().strftime("%w")) - 1, event, client, s, chat_id)

        elif event.data == b"entire_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(-10, event, client, s, chat_id)

        elif event.data == b"monday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(0, event, client, s, chat_id)

        elif event.data == b"tuesday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(1, event, client, s, chat_id)

        elif event.data == b"wednesday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(2, event, client, s, chat_id)

        elif event.data == b"thursday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(3, event, client, s, chat_id)

        elif event.data == b"friday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(4, event, client, s, chat_id)

        elif event.data == b"saturday_homework":
            await event.answer("Under development", alert=False)
            # await send_certain_day_homework(5, event, client, s, chat_id)


    @client.on(events.CallbackQuery(data=b"main_page"))
    async def main_page(event: events.CallbackQuery.Event):
        await to_main_page(event=event)


    @client.on(events.CallbackQuery(data=b"schedule_page"))
    async def schedule_page(event: events.CallbackQuery.Event):
        await to_schedule_page(event=event)


    @client.on(events.CallbackQuery(data=b"homework_page"))
    async def homework_page(event: events.CallbackQuery.Event):
        await to_homework_page(event=event)


    @client.on(events.CallbackQuery(data=b"certain_day_schedule"))
    async def certain_day_schedule(event: events.CallbackQuery.Event):
        await to_certain_day_schedule_page(event=event)


    @client.on(events.CallbackQuery(data=b"certain_day_homework"))
    async def certain_day_homework(event: events.CallbackQuery.Event):
        await to_certain_day_homework_page(event=event)


    @client.on(events.CallbackQuery(data=b"holidays"))
    async def holidays(event: events.CallbackQuery.Event):
        await asyncio.gather(event.answer("", alert=False),
                             send_holidays(client=client, sender=await event.get_sender()))


    @client.on(events.CallbackQuery(data=b"marks"))
    async def marks(event: events.CallbackQuery.Event):
        await event.answer("Under development", alert=False)


    @client.on(events.NewMessage())
    async def handle_new_messages(event: events.NewMessage.Event):
        sender = await event.get_sender()
        chat_id: str = str(sender.id)

        if event.message.message.lower() == "clear previous":
            _, msg = await asyncio.gather(event.delete(), get_message_sql(chat_id=chat_id, conn=connection, c=cursor))
            msg_ids: list[int] = [i for i in range(msg, event.message.id)]

            try:
                await client.delete_messages(entity=sender, message_ids=msg_ids)
            except errors.common.MultiError or errors.MessageDeleteForbiddenError:
                pass

        elif event.message.message.lower() != "start":
            await event.delete()


    if __name__ == "__main__":
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()
