import re

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import run_sequence, run_parallel, Firestore, Postgresql


async def init(client: Client, cbQuery: CallbackQuery, db: Postgresql, fs: Firestore):
    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*options")))
    async def _options_page(_client: Client, message: types.Message):
        sender = message.from_user
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
            raise pyrogram.StopPropagation

        await run_parallel(
            cbQuery.send_main_page(sender=sender),
            db.increase_options_counter(sender_id=sender_id)
        )
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*start")))
    async def _start_page(_client: Client, message: types.Message):
        # if len(message.split()) == 2:
        #     auth_hash = event.message.message.split()[1]
        #     log.info(auth_hash)  # TODO auth
        sender: types.User = message.from_user
        sender_id = str(sender.id)

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender),
                cbQuery.send_help_page(sender=sender),
            ),
            fs.update_data(sender_id=sender_id, lang=sender.language_code),
            fs.update_name(sender_id=sender_id, first_name=sender.first_name, last_name=sender.last_name),
        )
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(re.compile(r"^main_page$")))
    async def _main_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_main_page(event=callback_query)
        raise pyrogram.StopPropagation

    # @client.on(events.CallbackQuery(pattern=b"set"))
    # async def _set_account(event: events.CallbackQuery.Event):
    #     await cbQuery.set_account(event)
    #     raise events.StopPropagation
    #
    # @client.on(events.CallbackQuery(pattern=b"remove"))
    # async def _remove_account(event: events.CallbackQuery.Event):
    #     await cbQuery.remove_account(event=event)
    #     raise events.StopPropagation

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*about")))
    async def _about_page(_client: Client, message: types.Message):
        sender: types.User = message.from_user
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
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*web")))
    async def _options_and_settings_page(_client: Client, message: types.Message):
        sender = message.from_user
        await _client.send_message(
            chat_id=sender.id,
            text="lol",
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton(
                    text="web app", web_app=types.WebAppInfo(url="http://0.0.0.0:8000/login.html?sender_id=123")
                )
            ]]),
        )
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*help")))
    async def _help_page(_client: Client, message: types.Message):
        sender: types.User = message.from_user
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
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(pattern=re.compile(r"^close$")))
    async def _handle_close(_client: Client, callback_query: types.CallbackQuery):
        sender: types.User = callback_query.from_user
        sender_id = str(sender.id)
        _, msg_ids_to_delete = await run_parallel(
            callback_query.edit_message_reply_markup(reply_markup=None),
            db.get_msg_ids(sender_id=sender_id)
        )
        await client.delete_messages(sender.id, tuple(map(int, msg_ids_to_delete.split())))
        raise pyrogram.StopPropagation
