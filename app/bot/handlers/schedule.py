import datetime
import functools as ft

from telethon import events, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import AnalyticsDatabase, Weekdays
from app.schemas import User


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: AnalyticsDatabase):
    @client.on(events.CallbackQuery(data=b"schedule_page"))
    async def _schedule_page(event: events.CallbackQuery.Event):
        await cbQuery.to_schedule_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"specific_day_schedule"))
    async def _specific_day_schedule(event: events.CallbackQuery.Event):
        await cbQuery.to_specific_day_schedule_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(pattern=r"(?i).*schedule"))
    async def _schedule(event: events.CallbackQuery.Event):
        sender: User = await event.get_sender()
        sender_id = str(sender.id)
        send_schedule = ft.partial(
            cbQuery.send_schedule,
            event=event
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
