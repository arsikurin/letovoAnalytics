#!/usr/bin/python3.10

import essential
import re
import asyncio
import datetime
import logging as log

from functools import partial
from telethon import TelegramClient, events, errors
from requests_futures.sessions import FuturesSession
from constants import API_ID, API_HASH, BOT_TOKEN
from classes.callbackquery import CallbackQuery
from classes.inlinequery import InlineQuery
from classes.enums import Weekdays, MarkTypes, PatternMatching
from classes.database import Database
from classes.firebase import Firebase

client = TelegramClient("letovoAnalytics", API_ID, API_HASH)
db: Database = ...
cbQuery = CallbackQuery(c=client)
iQuery = InlineQuery()


@essential.execute_immediately
async def _establish_connection():
    global db
    log.debug("established connection to the Postgres")
    db = await Database.create()


# TODO aiohttp
with FuturesSession() as session:
    asyncio.set_event_loop(asyncio.new_event_loop())


    @client.on(events.NewMessage(pattern=r"(?i).*options"))
    async def _options(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        _, ii = await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            Firebase.is_inited(sender_id=sender_id),
        )

        if not ii:
            await cbQuery.send_init_message(sender=sender)

            if not await db.is_inited(sender_id=sender_id):
                await asyncio.gather(
                    db.init_user(sender_id=sender_id),
                    db.increase_options_counter(sender_id=sender_id)
                )
            raise events.StopPropagation

        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await asyncio.gather(
            cbQuery.send_main_page(sender=sender),
            db.set_message_id(sender_id=sender_id, message_id=event.message.id + 3),
            db.increase_options_counter(sender_id=sender_id)
        )
        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def _start(event: events.NewMessage.Event):
        if len(event.message.message.split()) == 2:
            auth_hash = event.message.message.split()[1]
            log.info(auth_hash)  # TODO auth
        sender = await event.get_sender()
        sender_id = str(sender.id)
        await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_init_message(sender=sender),
            Firebase.update_data(sender_id=sender_id, lang=sender.lang_code),
            Firebase.update_name(sender_id=sender_id, first_name=sender.first_name, last_name=sender.last_name),
        )
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        await db.set_message_id(sender_id=sender_id, message_id=event.message.id + 3)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"main_page"))
    async def _main_page(event: events.CallbackQuery.Event):
        await cbQuery.to_main_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"schedule_page"))
    async def _schedule_page(event: events.CallbackQuery.Event):
        await cbQuery.to_schedule_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"homework_page"))
    async def _homework_page(event: events.CallbackQuery.Event):
        await cbQuery.to_homework_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"marks_page"))
    async def _marks_page(event: events.CallbackQuery.Event):
        await cbQuery.to_marks_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"specific_day_schedule"))
    async def _specific_day_schedule(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_schedule_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"specific_day_homework"))
    async def _specific_day_homework(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_homework_page(event=event)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(data=b"holidays"))
    async def _holidays(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        await asyncio.gather(
            event.answer(),
            cbQuery.send_holidays(sender=await event.get_sender()),
            db.increase_holidays_counter(sender_id=sender_id)
        )
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def _schedule(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        send_schedule = partial(
            cbQuery.send_schedule,
            event=event, s=session
        )
        match event.data:
            case b"today_schedule":
                await send_schedule(specific_day=Weekdays(int(datetime.datetime.now().strftime("%w"))))
            case b"entire_schedule":
                await send_schedule(specific_day=Weekdays.ALL)
            case b"monday_schedule":
                await send_schedule(specific_day=Weekdays.Monday)
            case b"tuesday_schedule":
                await send_schedule(specific_day=Weekdays.Tuesday)
            case b"wednesday_schedule":
                await send_schedule(specific_day=Weekdays.Wednesday)
            case b"thursday_schedule":
                await send_schedule(specific_day=Weekdays.Thursday)
            case b"friday_schedule":
                await send_schedule(specific_day=Weekdays.Friday)
            case b"saturday_schedule":
                await send_schedule(specific_day=Weekdays.Saturday)
        await db.increase_schedule_counter(sender_id=sender_id)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*homework"))
    async def _homework(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        send_homework = partial(
            cbQuery.send_homework,
            event=event, s=session
        )
        match event.data:
            case b"tomorrows_homework":
                await send_homework(specific_day=Weekdays(int(datetime.datetime.now().strftime("%w")) + 1))
            case b"entire_homework":
                await send_homework(specific_day=Weekdays.ALL)
            case b"monday_homework":
                await send_homework(specific_day=Weekdays.Monday)
            case b"tuesday_homework":
                await send_homework(specific_day=Weekdays.Tuesday)
            case b"wednesday_homework":
                await send_homework(specific_day=Weekdays.Wednesday)
            case b"thursday_homework":
                await send_homework(specific_day=Weekdays.Thursday)
            case b"friday_homework":
                await send_homework(specific_day=Weekdays.Friday)
            case b"saturday_homework":
                await send_homework(specific_day=Weekdays.Saturday)
        await db.increase_homework_counter(sender_id=sender_id)
        raise events.StopPropagation


    @client.on(events.CallbackQuery(pattern=r"(?i).*marks"))
    async def _marks(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        send_marks = partial(
            cbQuery.send_marks,
            event=event, s=session
        )
        match event.data:
            case b"all_marks":
                await send_marks(specific=MarkTypes.ALL)
            case b"summative_marks":
                await send_marks(specific=MarkTypes.Only_summative)
            case b"recent_marks":
                await event.answer("Under development")
                # await send_marks(specific=MarkTypes.Recent)
        await db.increase_marks_counter(sender_id=sender_id)
        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*about"))
    async def _about(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            db.set_message_id(sender_id=sender_id, message_id=event.message.id + 3),
            db.increase_about_counter(sender_id=sender_id),
            cbQuery.send_about_message(sender=sender)
        )

        raise events.StopPropagation


    @client.on(events.NewMessage(pattern=r"(?i).*help"))
    async def _help(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await asyncio.gather(
            cbQuery.send_greeting(sender=sender),
            db.set_message_id(sender_id=sender_id, message_id=event.message.id + 3),
            db.increase_help_counter(sender_id=sender_id),
            cbQuery.send_help_message(sender=sender)
        )
        raise events.StopPropagation


    @client.on(events.NewMessage())
    async def _delete(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)

        if re.fullmatch(r"(?i).*clear previous", f"{event.message.message}"):
            _, msg, _ = await asyncio.gather(
                event.delete(),
                db.get_message_id(sender_id=sender_id),
                db.increase_clear_counter(sender_id=sender_id)
            )
            msg_ids: list[int] = [i for i in range(msg, event.message.id)]

            try:
                await client.delete_messages(entity=sender, message_ids=msg_ids)
            except (errors.common.MultiError, errors.MessageDeleteForbiddenError):
                pass
            raise events.StopPropagation
        await event.delete()


    @client.on(events.InlineQuery())
    async def _inline_query(event: events.InlineQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)

        if not await Firebase.is_inited(sender_id=sender_id):
            await event.answer(switch_pm="Log in", switch_pm_param="inlineMode")
            raise events.StopPropagation

        send_schedule = partial(
            iQuery.send_schedule,
            event=event, s=session
        )
        match PatternMatching(event.query.query):
            case PatternMatching(next=True):
                # TODO next day inline query
                await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
                # await event.answer([
                #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics rn")
                # ], switch_pm="Log in", switch_pm_param="inlineMode")
            case PatternMatching(today=True):
                await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
            case PatternMatching(monday=True):
                await send_schedule(specific_day=Weekdays.Monday.value)
            case PatternMatching(tuesday=True):
                await send_schedule(specific_day=Weekdays.Tuesday.value)
            case PatternMatching(wednesday=True):
                await send_schedule(specific_day=Weekdays.Wednesday.value)
            case PatternMatching(thursday=True):
                await send_schedule(specific_day=Weekdays.Thursday.value)
            case PatternMatching(friday=True):
                await send_schedule(specific_day=Weekdays.Friday.value)
            case PatternMatching(saturday=True):
                await send_schedule(specific_day=Weekdays.Saturday.value)
            case PatternMatching(entire=True):
                await send_schedule(specific_day=Weekdays.ALL.value)
            case _:
                await iQuery.to_main_page(event=event)


    if __name__ == "__main__":
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()
