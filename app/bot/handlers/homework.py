import datetime
import functools as ft

from telethon import events, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import AnalyticsDatabase, Weekdays
from app.schemas import User


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: AnalyticsDatabase):
    @client.on(events.CallbackQuery(data=b"homework_page"))
    async def _homework_page(event: events.CallbackQuery.Event):
        await cbQuery.to_homework_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"specific_day_homework"))
    async def _specific_day_homework(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_homework_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(pattern=r"(?i).*homework"))
    async def _homework(event: events.CallbackQuery.Event):
        sender: User = await event.get_sender()
        sender_id = str(sender.id)
        send_homework = ft.partial(
            cbQuery.send_homework,
            event=event
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
