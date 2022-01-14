import datetime
import functools as ft
import logging as log

from telethon import events, types, TelegramClient

from app.bot import InlineQuery
from app.dependencies import types as types_l, CredentialsDatabase


async def init(client: TelegramClient, iQuery: InlineQuery, fs: CredentialsDatabase):
    log.info("iquery currently out of date. Therefore, it is disabled")
    return

    @client.on(events.InlineQuery())  # TODO NOT WORKING CURRENTLY
    async def _inline_query(event: events.InlineQuery.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)

        if not await fs.is_inited(sender_id=sender_id):
            await event.answer(switch_pm="Log in", switch_pm_param="inlineMode")
            raise events.StopPropagation

        send_schedule = ft.partial(
            iQuery.send_schedule,
            event=event
        )
        match types_l.PatternMatching(event.query.query):
            case types_l.PatternMatching(next=True):
                # TODO next day inline query
                await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
                # await event.answer([
                #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics")
                # ], switch_pm="Log in", switch_pm_param="inlineMode")
            case types_l.PatternMatching(today=True):
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
