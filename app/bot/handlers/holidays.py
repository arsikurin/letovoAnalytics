from telethon import events, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import AnalyticsDatabase, run_parallel
from app.schemas import User


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: AnalyticsDatabase):
    @client.on(events.CallbackQuery(data=b"holidays"))
    async def _holidays(event: events.CallbackQuery.Event):
        sender: User = await event.get_sender()
        sender_id = str(sender.id)
        await run_parallel(
            event.answer(),
            cbQuery.send_holidays(event=event),
            db.increase_holidays_counter(sender_id=sender_id)
        )
        raise events.StopPropagation
