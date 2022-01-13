from telethon import events, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import run_sequence
from app.schemas import User


async def init(client: TelegramClient, cbQuery: CallbackQuery):
    @client.on(events.NewMessage(pattern=r"#dev", from_users=(606336225,)))
    async def _dev(event: events.NewMessage.Event):
        sender: User = await event.get_sender()
        await run_sequence(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_dev_page(sender=sender)
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"stats"))
    async def _stats(event: events.CallbackQuery.Event):
        sender: User = await event.get_sender()
        await run_sequence(
            cbQuery.send_stats_page(sender=sender),
            event.answer("Done")
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"tokens"))
    async def _tokens(event: events.CallbackQuery.Event):
        sender: User = await event.get_sender()
        sender_id = str(sender.id)
        if sender_id not in ("606336225",):
            raise events.StopPropagation
        from app.helper import main
        await main()
        await event.answer("Tokens updated in the Database")
        raise events.StopPropagation
