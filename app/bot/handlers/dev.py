import asyncio
import datetime
import time

from telethon import events, types, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import run_sequence, run_parallel


async def init(client: TelegramClient, cbQuery: CallbackQuery):
    @client.on(events.NewMessage(pattern=r"#dev", from_users=(606336225,)))
    async def _dev(event: events.NewMessage.Event):
        sender: types.User = await event.get_sender()
        await run_sequence(
            cbQuery.send_greeting(sender=sender),
            cbQuery.send_dev_page(sender=sender)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern="#ping", forwards=False))
    async def _ping(event: events.NewMessage.Event):
        start_time = time.perf_counter()
        message = await event.reply("Pong!")
        took = datetime.timedelta(seconds=time.perf_counter() - start_time)
        await run_parallel(
            event.delete(),
            run_sequence(
                message.edit(f"Pong! __(reply took {took.total_seconds()}s)__"),
                asyncio.sleep(5),
                message.delete()
            )
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"stats"))
    async def _stats(event: events.CallbackQuery.Event):
        sender: types.User = await event.get_sender()
        await run_sequence(
            cbQuery.send_stats(sender=sender),
            event.answer("Done")
        )
        raise events.StopPropagation

    @client.on(events.CallbackQuery(data=b"tokens"))
    async def _tokens(event: events.CallbackQuery.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)
        if sender_id not in ("606336225",):
            raise events.StopPropagation
        from app.helper import main
        await main()
        await event.answer("Tokens updated in the Database")
        raise events.StopPropagation
