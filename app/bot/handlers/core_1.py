import logging as log

from telethon import events, types, TelegramClient

from app.bot import CallbackQuery
from app.dependencies import run_sequence, run_parallel, Firestore, Postgresql


async def init(client: TelegramClient, cbQuery: CallbackQuery, db: Postgresql, fs: Firestore):
    @client.on(events.NewMessage(pattern=r"(?i).*(options|settings)"))
    async def _options_and_settings_page(event: events.NewMessage.Event):
        sender: types.User = await event.get_sender()
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

        if event.message.message == "Options":
            response_func = cbQuery.send_main_page
        else:
            response_func = cbQuery.send_settings_page

        await run_parallel(
            response_func(sender=sender),
            db.increase_options_counter(sender_id=sender_id)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def _start_page(event: events.NewMessage.Event):
        if len(event.message.message.split()) == 2:
            auth_hash = event.message.message.split()[1]
            log.info(auth_hash)  # TODO auth
        sender: types.User = await event.get_sender()
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

    @client.on(events.CallbackQuery(data=b"main_page"))
    async def _main_page(event: events.CallbackQuery.Event):
        await cbQuery.to_main_page(event=event)
        raise events.StopPropagation

    # @client.on(events.CallbackQuery(pattern=b"set"))
    # async def _set_account(event: events.CallbackQuery.Event):
    #     await cbQuery.set_account(event)
    #     raise events.StopPropagation
    #
    # @client.on(events.CallbackQuery(pattern=b"remove"))
    # async def _remove_account(event: events.CallbackQuery.Event):
    #     await cbQuery.remove_account(event=event)
    #     raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*about"))
    async def _about_page(event: events.NewMessage.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender),
                cbQuery.send_about_page(sender=sender)
            ),
            db.increase_about_counter(sender_id=sender_id)
        )
        raise events.StopPropagation

    @client.on(events.NewMessage(pattern=r"(?i).*help"))
    async def _help_page(event: events.NewMessage.Event):
        sender: types.User = await event.get_sender()
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

    @client.on(events.CallbackQuery(data=b"close"))
    async def _handle_close(event: events.CallbackQuery.Event):
        sender: types.User = await event.get_sender()
        sender_id = str(sender.id)
        _, msg_ids_to_delete = await run_parallel(
            event.edit(buttons=None),
            db.get_msg_ids(sender_id=sender_id)
        )

        await client.delete_messages(sender, tuple(map(int, msg_ids_to_delete.split())))
        raise events.StopPropagation
