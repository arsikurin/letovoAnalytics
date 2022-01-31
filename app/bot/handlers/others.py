from telethon import events, TelegramClient, types

from app.bot import CallbackQuery
from app.dependencies import AnalyticsDatabase, run_parallel


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: AnalyticsDatabase):
    @client.on(events.CallbackQuery(data=b"others_page"))
    async def _others_page(event: events.CallbackQuery.Event):
        await cbQuery.to_others_page(event=event)
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"teachers"))
    async def _teachers(event: events.CallbackQuery.Event):
        await run_parallel(
            cbQuery.send_teachers(event=event),
            # db.increase_teachers_counter(sender_id=sender_id)
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"diploma"))
    async def _diploma(event: events.CallbackQuery.Event):
        # await run_parallel(
        #     cbQuery.send_...(event=event),
        #     # db.increase_..._counter(sender_id=sender_id)
        # )
        await event.answer("Not implemented!")
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"holidays"))
    async def _holidays(event: events.CallbackQuery.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)
        await run_parallel(
            cbQuery.send_holidays(event=event),
            db.increase_holidays_counter(sender_id=sender_id)
        )
        raise events.StopPropagation
