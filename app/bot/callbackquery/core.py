#  Made by arsikurin in 2022.

from pyrogram import Client, types

from app.bot.callbackquery.base import CBQueryBase

choose_an_option_below_text = "Choose an option below ↴"


class CBQCore(CBQueryBase):
    async def send_greeting(self, sender: types.User, client: Client | None = None) -> types.Message:
        """
        Send a greeting to the end user

        Args:
            sender (types.User): end user
            client (Client | None): custom client

        Returns:
            types.Message
        """
        if client is None:
            client = self.client

        payload = f'{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}'.strip()
        return await client.send_message(
            chat_id=sender.id,
            text=f"Greetings, **{payload}**!",
            reply_markup=types.ReplyKeyboardMarkup([
                [
                    types.KeyboardButton("Options")
                ]
            ], resize_keyboard=True)
        )

    async def send_help_page(
            self, sender: types.User, no_register: bool = False, client: Client | None = None
    ) -> types.Message:
        """
        Send help page

        Args:
            sender (types.User): end user
            no_register (bool): either add button for registering or not
            client (Client | None): custom client

        Returns:
            types.Message
        """
        if client is None:
            client = self.client

        if not no_register:
            reply_markup = types.ReplyKeyboardMarkup([
                [
                    types.KeyboardButton(
                        text="Click here to register",
                        web_app=types.WebAppInfo(url="https://letovo-analytics.web.app/webview")
                    )
                ]
            ], resize_keyboard=True)
        else:
            reply_markup = None

        return await client.send_message(
            chat_id=sender.id,
            text="I can help you access s.letovo.ru resources via Telegram.\n"
                 "If you're new here, please see the [Terms of Use](https://example.com) and "
                 "provide your **school** credentials, i.e. login and password,"
                 " to begin enjoying the service.\n"
                 "To do this, click the **button below**.\n"
                 "\n"
                 "\n"
                 "**You can control the bot by sending these commands**\n"
                 "\n"
                 "Common:\n"
                 "**/start** — restart bot. You'll get a welcome message\n"
                 "**/about** — get info about the bot developers\n"
                 "**/options** — get a menu of options that the bot can serve\n"
                 "**/help** — get this manual page\n"
                 "\n"
                 "School info:\n"
                 "**/options » Schedule** — get schedule\n"
                 "**/options » Marks** — get marks\n"
                 "**/options » Homework** — get homework\n"
                 "__***homework** might not be displayed properly currently as it is in beta__\n"
                 "\n"
                 "Other info:\n"
                 "**/options » Others » Teachers' info** — get teachers' names and emails\n"
                 "**/options » Others » Subscribe to schedule** — receive latest schedule everyday\n"
                 "**/options » Others » Holidays** — get holidays periods\n"
                 "\n"
                 "\n"
                 "**Bot Settings**\n"
                 "__coming soon__\n"
                 "\n"
                 "\n"
                 "**Marks CI**\n"
                 "From **0** to **8** followed by a criterion:\n"
                 "**A**, **B**, **C** or **D** — Summative marks\n"
                 "**F** — Formative marks\n"
                 "\n"
                 "__For example:__\n"
                 "• **7A** means **7** for Summative **A**\n"
                 "• **5B** means **5** for Summative **B**\n"
                 "• **6F** means **6** for Formative\n",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

    async def send_about_page(self, sender: types.User) -> types.Message:
        """
        Send `about developers` page

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        return await self.client.send_message(
            chat_id=sender.id,
            text="**Arseny Kurin**\n\n"
                 "• 2024kurin.av@student.letovo.ru\n"
                 "• [Github](https://github.com/arsikurin)\n"
                 "• [Telegram](https://t.me/arsikurin)\n",
        )

    async def send_landing_page(self, sender: types.User) -> types.Message:
        """
        Send landing page

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        return await self.client.send_message(
            chat_id=sender.id,
            text=choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Schedule »", b"schedule_page")
                ], [
                    types.InlineKeyboardButton("Homework »", b"homework_page"),
                ], [
                    types.InlineKeyboardButton("Marks »", b"marks_page"),
                ], [
                    types.InlineKeyboardButton("Others »", b"others_page"),
                ]
            ])
        )

    @staticmethod
    async def to_landing_page(event: types.CallbackQuery):
        """
        Display `landing` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Schedule »", b"schedule_page")
                ], [
                    types.InlineKeyboardButton("Homework »", b"homework_page"),
                ], [
                    types.InlineKeyboardButton("Marks »", b"marks_page"),
                ], [
                    types.InlineKeyboardButton("Others »", b"others_page"),
                ]
            ])
        )
        await event.answer()
