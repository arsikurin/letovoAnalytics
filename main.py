#!/usr/bin/python3.9

import re
import asyncio
import psycopg2
import datetime
# import time
# import logging as log

from functools import partial
from telethon import TelegramClient, events, errors
from requests_futures.sessions import FuturesSession
from essential import (
    HOST_SQL,
    PORT_SQL,
    USER_SQL,
    DATABASE_SQL,
    PASSWORD_SQL,
    API_ID,
    API_HASH,
    BOT_TOKEN,
    Database,  # SQL db for clearing messages
    Firebase,  # NoSQL db for the other data
    CallbackQuery,
    InlineQuery,
    Weekdays
)

with FuturesSession() as session:
    with psycopg2.connect(
            host=HOST_SQL, port=PORT_SQL, user=USER_SQL, database=DATABASE_SQL, password=PASSWORD_SQL, sslmode="require"
    ) as connection:
        cursor = connection.cursor()
    client = TelegramClient("letovoAnalytics", API_ID, API_HASH)
    cbQuery = CallbackQuery(c=client)
    iQuery = InlineQuery()
    db = Database(conn=connection, c=cursor)


    @client.on(events.NewMessage(pattern=r"(?i).*options"))
    async def options(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        _, ii = await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            Firebase.is_inited(sender_id=sender_id)
        )

        if not ii:
            await cbQuery.send_init_message(sender=sender)

            if not await db.is_inited(sender_id=sender_id):
                await db.init_user(sender_id=sender_id)
            raise events.StopPropagation

        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await asyncio.gather(
            cbQuery.send_main_page(sender=sender),
            db.set_message(sender_id=sender_id, message_id=event.message.id + 3)
        )
        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def start(event: events.NewMessage.Event):
        if len(event.message.message.split()) == 2:
            auth_hash = event.message.message.split()[1]
            print(auth_hash)  # TODO auth
        sender = await event.get_sender()
        sender_id = str(sender.id)
        await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_init_message(sender=sender),
            Firebase.update_data(sender_id=sender_id, lang=sender.lang_code),
            Firebase.update_name(sender_id=sender_id, first_name=sender.first_name, last_name=sender.last_name)
        )

        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        await db.set_message(sender_id=sender_id, message_id=event.message.id + 3)
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
            cbQuery.send_holidays(sender=await event.get_sender())
        )
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"marks"))
    async def marks(event: events.CallbackQuery.Event):
        await event.answer("Under development", alert=False)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def schedule(event: events.CallbackQuery.Event):
        send_specific_day_schedule = partial(
            cbQuery.send_specific_day_schedule,
            event=event, s=session
        )

        if event.data == b"todays_schedule":
            await send_specific_day_schedule(specific_day=int(datetime.datetime.now().strftime("%w")) - 1)

        elif event.data == b"entire_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.ALL.value)

        elif event.data == b"monday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Monday.value - 1)

        elif event.data == b"tuesday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Tuesday.value - 1)

        elif event.data == b"wednesday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Wednesday.value - 1)

        elif event.data == b"thursday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Thursday.value - 1)

        elif event.data == b"friday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Friday.value - 1)

        elif event.data == b"saturday_schedule":
            await send_specific_day_schedule(specific_day=Weekdays.Saturday.value - 1)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*homework"))
    async def homework(event: events.CallbackQuery.Event):
        send_specific_day_homework = partial(
            cbQuery.send_specific_day_homework,
            event=event, s=session
        )
        if event.data == b"tomorrows_homework":
            await send_specific_day_homework(specific_day=int(datetime.datetime.now().strftime("%w")) + 1)

        elif event.data == b"entire_homework":
            await send_specific_day_homework(specific_day=Weekdays.ALL.value)

        elif event.data == b"monday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Monday.value)

        elif event.data == b"tuesday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Tuesday.value)

        elif event.data == b"wednesday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Wednesday.value)

        elif event.data == b"thursday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Thursday.value)

        elif event.data == b"friday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Friday.value)

        elif event.data == b"saturday_homework":
            await send_specific_day_homework(specific_day=Weekdays.Saturday.value)
        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*about"))
    async def about(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            db.set_message(sender_id=sender_id, message_id=event.message.id + 3),
            cbQuery.send_about_message(sender=sender)
        )

        raise events.StopPropagation


    @client.on(events.NewMessage())
    async def delete(event: events.NewMessage.Event):
        sender = await event.get_sender()

        if re.fullmatch(r"(?i).*clear previous", f"{event.message.message}"):
            _, msg = await asyncio.gather(
                event.delete(),
                db.get_message(sender_id=str(sender.id))
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

        if not await Firebase.is_inited(sender_id=sender_id):
            await event.answer(switch_pm="Log in", switch_pm_param="inlineMode")
            raise events.StopPropagation

        send_specific_day_schedule = partial(
            iQuery.send_specific_day_schedule,
            event=event, s=session, sender_id=sender_id
        )

        if re.match(r"ne", f"{event.query.query}"):
            # TODO next day inline query
            await send_specific_day_schedule(specific_day=int(datetime.datetime.now().strftime("%w")) - 1)
            # await event.answer([
            #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics rn")
            # ], switch_pm="Log in", switch_pm_param="inlineMode")

        elif re.match(r"to", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=int(datetime.datetime.now().strftime("%w")) - 1)

        elif re.match(r"mo", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Monday.value - 1)

        elif re.match(r"tu", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Tuesday.value - 1)

        elif re.match(r"we", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Wednesday.value - 1)

        elif re.match(r"th", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Thursday.value - 1)

        elif re.match(r"fr", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Friday.value - 1)

        elif re.match(r"sa", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.Saturday.value - 1)

        elif re.match(r"en", f"{event.query.query}"):
            await send_specific_day_schedule(specific_day=Weekdays.ALL.value)

        else:
            await iQuery.to_main_page(event=event)


    if __name__ == "__main__":
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()
