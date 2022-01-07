import datetime
import functools as ft
import logging as log

import aiohttp
from telethon import events

from app.bot import CallbackQuery, InlineQuery, client
from app.dependencies import (
    Weekdays, MarkTypes, PatternMatching, run_sequence, run_parallel, AnalyticsDatabase, CredentialsDatabase
)

"""add client.add_event_handler, i.e. plugin architecture"""


# client.add_event_handler()

async def include_handlers(session: aiohttp.ClientSession, db: AnalyticsDatabase, fs: CredentialsDatabase):
    cbQuery = CallbackQuery(client=client, session=session)
    iQuery = InlineQuery(s=session)

    @client.on(events.NewMessage(pattern=r"(?i).*dev"))
    async def _dev(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if sender_id not in ("606336225", "644775011", "1381048606", "757953400"):
            raise events.StopPropagation
        await run_sequence(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_dev_page(sender=sender)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*options"))
    async def _options(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        _, il = await run_parallel(
            cbQuery.send_greeting(sender=sender),
            fs.is_logged(sender_id=sender_id),
        )
        if not il:
            _, ii = await run_parallel(
                cbQuery.send_help_page(sender=sender),
                db.is_inited(sender_id=sender_id)
            )
            if not ii:
                await db.init_user(sender_id=sender_id)

            await db.increase_options_counter(sender_id=sender_id)
            raise events.StopPropagation

        await run_parallel(
            cbQuery.send_main_page(sender=sender),
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

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender),
                cbQuery.send_help_page(sender=sender),
            ),
            fs.update_data(sender_id=sender_id, lang=sender.lang_code),
            fs.update_name(sender_id=sender_id, first_name=sender.first_name, last_name=sender.last_name),
        )
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"stats"))
    async def _stats(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        await run_sequence(
            cbQuery.send_stats_page(sender=sender, db=db, fs=fs),
            event.answer("Done")
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"tokens"))
    async def _tokens(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if sender_id not in ("606336225",):
            raise events.StopPropagation
        from app.helper import main
        await main()
        await event.answer("Tokens updated in the Database")
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
        await run_parallel(
            event.answer(),
            cbQuery.send_holidays(event=event),
            db.increase_holidays_counter(sender_id=sender_id)
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def _schedule(event: events.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        send_schedule = ft.partial(
            cbQuery.send_schedule,
            event=event, fs=fs
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
        send_homework = ft.partial(
            cbQuery.send_homework,
            event=event, fs=fs
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
        send_marks = ft.partial(
            cbQuery.send_marks,
            event=event, fs=fs
        )
        match event.data:
            case b"all_marks":
                await send_marks(specific=MarkTypes.ALL)
            case b"summative_marks":
                await send_marks(specific=MarkTypes.SUMMATIVE)
            case b"final_marks":
                await send_marks(specific=MarkTypes.FINAL)
            case b"recent_marks":
                await event.answer("Under development")
                # await send_marks(specific=MarkTypes.RECENT)
        await db.increase_marks_counter(sender_id=sender_id)
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*about"))
    async def _about(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        await run_sequence(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_about_page(sender=sender)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*help"))
    async def _help(event: events.NewMessage.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender),
                cbQuery.send_help_page(sender=sender)
            ),
            db.increase_help_counter(sender_id=sender_id)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage())
    async def _delete(event: events.NewMessage.Event):
        await event.delete()

    # @client.on(events.InlineQuery()) TODO NOT WORKING CURRENTLY
    async def _inline_query(event: events.InlineQuery.Event):
        sender = await event.get_sender()
        sender_id = str(sender.id)

        if not await fs.is_inited(sender_id=sender_id):
            await event.answer(switch_pm="Log in", switch_pm_param="inlineMode")
            raise events.StopPropagation

        send_schedule = ft.partial(
            iQuery.send_schedule,
            event=event, fs=fs
        )
        match PatternMatching(event.query.query):
            case PatternMatching(next=True):
                # TODO next day inline query
                await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
                # await event.answer([
                #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics")
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
