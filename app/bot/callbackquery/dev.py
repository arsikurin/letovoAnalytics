#  Made by arsikurin in 2022.

from pyrogram import types

from app.bot.callbackquery.base import CBQueryBase
from app.dependencies import run_parallel, errors as errors_l, types as types_l

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQueryDev(CBQueryBase):
    async def send_stats(self, sender: types.User):
        """
        Send usage statistics

        Args:
            sender (types.User): end user
        """
        for user in await self._db.get_users():
            resp = await self._db.get_analytics(user)
            if not any((
                    resp.schedule_counter, resp.homework_counter, resp.marks_counter, resp.holidays_counter,
                    resp.options_counter, resp.help_counter, resp.about_counter
            )): continue  # noqa: more beautiful imho

            namesurname, login = await run_parallel(
                self._fs.get_name(
                    sender_id=resp.sender_id, values=[types_l.FSNames.first_name, types_l.FSNames.last_name]
                ),
                self._fs.get_data(sender_id=resp.sender_id, values=[types_l.FSData.login])
            )

            name = namesurname[0] if namesurname[0] is not errors_l.NothingFoundError else ""
            surname = namesurname[1] if namesurname[1] is not errors_l.NothingFoundError else ""
            login = login[0] if login[0] is not errors_l.NothingFoundError else ""
            await self.client.send_message(
                chat_id=sender.id,
                text=f"ID: {resp.sender_id}\n"
                     f"Name: {name} {surname}\n"
                     f"Login: {login}\n"
                     f"Schedule: {resp.schedule_counter}\n"
                     f"Homework {resp.homework_counter}\n"
                     f"Marks: {resp.marks_counter}\n"
                     f"Holidays: {resp.holidays_counter}\n"
                     f"Options: {resp.options_counter}\n"
                     f"Help: {resp.help_counter}\n"
                     f"About: {resp.about_counter}",
            )

    async def send_dev_page(self, sender: types.User) -> types.Message:
        """
        Send page related to development

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
                    types.InlineKeyboardButton("Statistics", b"stats")
                ], [
                    types.InlineKeyboardButton("Update tokens", b"tokens"),
                ]
            ])
        )
