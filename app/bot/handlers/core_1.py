import json
import re

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery
from app.dependencies import run_sequence, run_parallel, Firestore, Postgresql, filters, types as types_l
from config import settings


async def init(clients: types_l.clients[Client], cbQuery: CallbackQuery, db: Postgresql, fs: Firestore):
    client = clients.client

    async def inline_or_regular(client_: Client, sender: types.User):
        if client_.name == "letovoAnalytics":
            await cbQuery.send_landing_page(sender=sender)
        else:
            await client_.send_message(
                chat_id=sender.id,
                text="**This bot is used only for inline query**, i.e. `@l3tovobot [query]`\n"
                     "\n"
                     "Consider following @LetovoAnalyticsBot link or return to where you left off",
                reply_markup=types.ReplyKeyboardMarkup([
                    [
                        types.KeyboardButton("Options")
                    ]
                ], resize_keyboard=True)
            )

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*options")))
    async def _options_page(_client: Client, message: types.Message):
        sender = message.from_user
        sender_id = str(sender.id)
        _, il = await run_parallel(
            cbQuery.send_greeting(sender=sender, client=_client),
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
            cbQuery.send_landing_page(sender=sender),
            db.increase_options_counter(sender_id=sender_id)
        )
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*start")))
    @clients.client_i.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*start")))
    async def _start_page(_client: Client, message: types.Message):
        # if len(message.split()) == 2:
        #     auth_hash = event.message.message.split()[1]
        #     log.info(auth_hash)  # TODO auth
        sender: types.User = message.from_user
        sender_id = str(sender.id)

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender, client=_client),
                cbQuery.send_help_page(sender=sender, client=_client),
            ),
            fs.update_data(sender_id=sender_id, lang=sender.language_code),
            fs.update_name(sender_id=sender_id, first_name=sender.first_name, last_name=sender.last_name),
        )
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)
        raise pyrogram.StopPropagation

    @client.on_message(pyrogram.filters.service & filters.web_app)
    @clients.client_i.on_message(pyrogram.filters.service & filters.web_app)
    async def _webapp_response_handler(_client: Client, message: types.Message):
        sender = message.from_user

        try:
            data = json.loads(message.web_app_data.data)
            await fs.update_data(
                sender_id=str(sender.id), student_id=data["studentID"], lang=sender.language_code,
                analytics_password=data["password"], analytics_login=data["login"], token=data["token"]
            )
            await run_parallel(
                run_sequence(
                    _client.send_message(
                        chat_id=sender.id,
                        text="__Successfully registered!__\n",
                        reply_markup=types.ReplyKeyboardMarkup([[
                            types.KeyboardButton("Options")
                        ]], resize_keyboard=True)
                    ),
                    inline_or_regular(_client, sender)
                ),
                fs.send_email_to(data["login"])
            )
        except Exception as err:
            await _client.send_message(
                chat_id=sender.id,
                text="**[✘] Something went wrong!**\n\nThis incident will be reported. Try again later"
            )
            await client.send_message(
                chat_id=606336225 if settings().production else 2200163963,
                text=f"**[✘] Error occurred!** ||ID={sender.id}||\n\n```"
                     f"{err.__repr__()=}\n{err.__traceback__=}\n{err.__doc__=}```"
            )
        raise pyrogram.StopPropagation

    @client.on_callback_query(pyrogram.filters.regex(pattern=re.compile(r"^main_page$")))
    async def _main_page(_client: Client, callback_query: types.CallbackQuery):
        await cbQuery.to_landing_page(event=callback_query)
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

    @client.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*help")))
    @clients.client_i.on_message(pyrogram.filters.regex(pattern=re.compile(r"(?i).*help")))
    async def _help_page(_client: Client, message: types.Message):
        sender: types.User = message.from_user
        sender_id = str(sender.id)
        if not await db.is_inited(sender_id=sender_id):
            await db.init_user(sender_id=sender_id)

        await run_parallel(
            run_sequence(
                cbQuery.send_greeting(sender=sender, client=_client),
                cbQuery.send_help_page(sender=sender, client=_client, no_register=True)
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
