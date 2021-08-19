#!/usr/bin/python3.9

import re
import asyncio
import sqlite3
# import datetime
# import time
# import logging as log

from requests_futures.sessions import FuturesSession
from datetime import date
from telethon import TelegramClient, events, errors
from essential import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    Database,
    Firebase,
    CallbackQuery as cbQuery,
    InlineQuery as iQuery,
)

"https://s-api.letovo.ru/api/students/54405"
"https://s-api.letovo.ru/api/studentsimg/54405"

client = TelegramClient("letovoAnalytics", API_ID, API_HASH)

with FuturesSession() as session:
    with sqlite3.Connection("users.sql") as connection:
        cursor = sqlite3.Cursor(connection)


    @client.on(events.NewMessage(pattern=r"(?i).*menu"))
    async def menu(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        _, ii = await asyncio.gather(
            cbQuery.send_greeting(client=client, sender=sender),
            Firebase.is_inited(sender_id=sender_id)
        )

        if not ii:
            await cbQuery.send_init_message(client=client, sender=sender)

            if not await Database.is_inited(sender_id=sender_id, conn=connection, c=cursor):
                await Database.init_user(sender_id=sender_id, conn=connection, c=cursor)
            raise events.StopPropagation

        if not await Database.is_inited(sender_id=sender_id, conn=connection, c=cursor):
            await Database.init_user(sender_id=sender_id, conn=connection, c=cursor)

        await asyncio.gather(
            cbQuery.send_main_page(client=client, sender=sender),
            Database.set_message(sender_id=sender_id, message_id=event.message.id + 3, conn=connection, c=cursor)
        )
        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def start(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        await asyncio.gather(
            cbQuery.send_greeting(client=client, sender=sender),
            cbQuery.send_init_message(client=client, sender=sender),
            Firebase.update_data(sender_id=sender_id, lang=sender.lang_code)
        )

        if not await Database.is_inited(sender_id=sender_id, conn=connection, c=cursor):
            await Database.init_user(sender_id=sender_id, conn=connection, c=cursor)
        await Database.set_message(sender_id=sender_id, message_id=event.message.id + 3, conn=connection, c=cursor)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def schedule(event: events.CallbackQuery.Event):
        sender_id: str = str(event.original_update.user_id)
        if event.data == b"todays_schedule":
            await cbQuery.send_specific_day_schedule(
                specific_day=int(date.today().strftime("%w")) - 1,
                event=event, client=client, s=session, sender_id=sender_id
            )
            raise events.StopPropagation

        elif event.data == b"entire_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=-10, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"monday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=0, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"tuesday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=1, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"wednesday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=2, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"thursday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=3, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"friday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=4, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation

        elif event.data == b"saturday_schedule":
            await cbQuery.send_specific_day_schedule(specific_day=5, event=event, client=client, s=session,
                                                     sender_id=sender_id)
            raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*homework"))
    async def homework(event: events.CallbackQuery.Event):
        sender_id: str = str(event.original_update.user_id)
        if event.data == b"tomorrows_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(int(date.today().strftime("%w")) - 1, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"entire_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(-10, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"monday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(0, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"tuesday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(1, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"wednesday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(2, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"thursday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(3, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"friday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(4, event, client, s, sender_id)
            raise events.StopPropagation

        elif event.data == b"saturday_homework":
            await event.answer("Under development", alert=False)
            # await send_specific_day_homework(5, event, client, s, sender_id)
            raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"main_page"))
    async def main_page(event: events.CallbackQuery.Event):
        await cbQuery.to_main_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"schedule_page"))
    async def schedule_page(event: events.CallbackQuery.Event):
        await cbQuery.to_schedule_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"homework_page"))
    async def homework_page(event: events.CallbackQuery.Event):
        await cbQuery.to_homework_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"specific_day_schedule"))
    async def specific_day_schedule(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_schedule_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"specific_day_homework"))
    async def specific_day_homework(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_homework_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"holidays"))
    async def holidays(event: events.CallbackQuery.Event):
        await asyncio.gather(
            event.answer(),
            cbQuery.send_holidays(client=client, sender=await event.get_sender())
        )
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"marks"))
    async def marks(event: events.CallbackQuery.Event):
        await event.answer("Under development", alert=False)
        raise events.StopPropagation


    @client.on(events.NewMessage())
    async def delete(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id: str = str(sender.id)

        if re.fullmatch(r"(?i).*clear previous", f"{event.message.message}"):
            _, msg = await asyncio.gather(
                event.delete(),
                Database.get_message(sender_id=sender_id, conn=connection, c=cursor)
            )
            msg_ids: list[int] = [i for i in range(msg, event.message.id)]

            try:
                await client.delete_messages(entity=sender, message_ids=msg_ids)
            except (errors.common.MultiError, errors.MessageDeleteForbiddenError):
                pass
            raise events.StopPropagation

        await event.delete()


    @client.on(events.InlineQuery())
    async def handle_inline_query(event: events.InlineQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        builder = event.builder

        if not await Firebase.is_inited(sender_id=sender_id):
            await event.answer(switch_pm="Log in", switch_pm_param="inlineMode")
            raise events.StopPropagation

        if re.match(r"ne", f"{event.query.query}"):
            # TODO next day inline query
            await iQuery.send_specific_day_schedule_inline(specific_day=0, s=session, event=event, sender_id=sender_id)
            # await event.answer([
            #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics rn")
            # ], switch_pm="Log in", switch_pm_param="inlineMode")

        elif re.match(r"to", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(
                specific_day=int(date.today().strftime("%w")) - 1,
                s=session, event=event, sender_id=sender_id
            )

        elif re.match(r"mo", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=0, s=session, event=event, sender_id=sender_id)

        elif re.match(r"tu", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=1, s=session, event=event, sender_id=sender_id)

        elif re.match(r"we", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=2, s=session, event=event, sender_id=sender_id)

        elif re.match(r"th", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=3, s=session, event=event, sender_id=sender_id)

        elif re.match(r"fr", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=4, s=session, event=event, sender_id=sender_id)

        elif re.match(r"sa", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=5, s=session, event=event, sender_id=sender_id)

        elif re.match(r"en", f"{event.query.query}"):
            await iQuery.send_specific_day_schedule_inline(specific_day=-10, s=session, event=event,
                                                           sender_id=sender_id)

        else:
            await iQuery.to_main_page_inline(event=event)


    if __name__ == "__main__":
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()
