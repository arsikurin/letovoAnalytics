#  Made by arsikurin in 2022.
import datetime

from pyrogram import types

from app.bot.callbackquery.base import CBQueryBase
from app.dependencies import errors as errors_l
from app.schemas import TeachersResponse
from config import settings

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQOthers(CBQueryBase):
    async def send_holidays(self, event: types.CallbackQuery):
        """
        Send holidays

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        # TODO receive holidays from API
        sender: types.User = event.from_user
        await self.client.send_message(
            chat_id=sender.id,
            text="__after__ **unit I**\n30.10.2021 — 06.11.2021",
        )

        await self.client.send_message(
            chat_id=sender.id,
            text="__after__ **unit II**\n24.12.2021 — 12.01.2022",
        )

        await self.client.send_message(
            chat_id=sender.id,
            text="__after__ **unit III**\n19.03.2022 — 26.03.2022",
        )

        await self.client.send_message(
            chat_id=sender.id,
            text="__after__ **unit IV**\n22.05.2022 — 31.08.2022",
        )
        await event.answer()

    async def send_teachers(
            self, event: types.CallbackQuery
    ):
        """
        Parse & send teachers' names

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        sender: types.User = event.from_user

        try:
            response = await self._handle_errors(self._api.receive_marks_and_teachers, event, sender)
        except errors_l.StopPropagation:
            return

        msg_ids = []
        teachers_response = TeachersResponse.parse_obj(response)
        for subject in teachers_response.data:
            if subject.group.group_teachers:
                if subject.group.subject.subject_name_eng:
                    subject_name = subject.group.subject.subject_name_eng
                else:
                    subject_name = subject.group.subject.subject_name
                payload = [f"**{subject_name} {subject.group.group_name}**\n"]

                for subject_teacher in subject.group.group_teachers:
                    t = subject_teacher.teacher
                    payload.append(f"{t.teacher_name} {t.teacher_fath} {t.teacher_surname}\n{t.teacher_mail}\n\n")

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text="".join(payload),
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)

        if msg_ids:
            msg = await self._send_close_message_teachers(sender)
            msg_ids.append(msg.id)
            await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

        await event.answer()

    async def _send_close_message_teachers(
            self, sender: types.User
    ) -> types.Message:
        return await self.client.send_message(
            chat_id=sender.id,
            text=f"__Teachers' info, {datetime.datetime.now(tz=settings().timezone):%d.%m.%Y}__\n",
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton("Close", b"close")
            ]]),
            disable_notification=True
        )

    @staticmethod
    async def to_others_page(event: types.CallbackQuery):
        """
        Display `others` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Teachers' info", b"teachers")
                ], [
                    types.InlineKeyboardButton(
                        "Subscribe to schedule",
                        url=f"https://letovo-analytics.web.app/get_ics?user_id={event.from_user.id}"
                    ),
                ], [
                    types.InlineKeyboardButton("Holidays", b"holidays"),
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"main_page")
                ]
            ])
        )
        await event.answer()
