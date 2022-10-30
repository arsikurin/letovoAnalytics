#  Made by arsikurin in 2022.

from pyrogram import types, enums

from app.bot.callbackquery.base import CBQueryBase
from app.dependencies import errors as errors_l, types as types_l
from app.schemas import ScheduleAndHWResponse

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQHomework(CBQueryBase):
    async def send_homework(
            self, event: types.CallbackQuery, specific_day: types_l.Weekdays
    ):
        """
        Parse & send homework

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
            specific_day (types_l.Weekdays): day of the week
        """
        if specific_day == types_l.Weekdays.SundayHW:
            return await event.answer("Congrats! Tomorrow's Sunday, no hw", show_alert=False)

        sender: types.User = event.from_user
        try:
            response = await self._handle_errors(self._api.receive_schedule_and_hw, event, sender, specific_day)
        except errors_l.StopPropagation:
            return
        await event.answer("Homework might not be displayed properly as it is in beta")

        homework_response = ScheduleAndHWResponse.parse_obj(response)
        old_wd = ""
        msg_ids = []
        for day in homework_response.data:
            wd = types_l.Weekdays(int(day.period_num_day)).name
            if specific_day == types_l.Weekdays.Week and wd != old_wd:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=f"\n==={wd}===\n",
                    disable_notification=True
                )
                msg_ids.append(msg.id)

            if day.schedules:
                flag = False

                if day.schedules[0].group.subject.subject_name_eng:
                    subject = day.schedules[0].group.subject.subject_name_eng
                else:
                    subject = day.schedules[0].group.subject.subject_name
                payload = (
                    f"{day.period_name}: <strong>{subject}</strong>\n"
                )
                if day.schedules[0].lessons:
                    if day.schedules[0].lessons[0].lesson_hw:
                        payload += f"{day.schedules[0].lessons[0].lesson_hw}\n"
                    else:
                        payload += "<em>No homework</em>\n"

                    if day.schedules[0].lessons[0].lesson_url:
                        flag = True
                        payload += f'<a href="{day.schedules[0].lessons[0].lesson_url}">Attached link</a>\n'

                    if day.schedules[0].lessons[0].lesson_hw_url:
                        flag = True
                        payload += f'<a href="{day.schedules[0].lessons[0].lesson_hw_url}">Attached hw link</a>\n'

                    if not flag:
                        payload += "<em>No links attached</em>\n"

                    if day.schedules[0].lessons[0].lesson_topic:
                        payload += f"{day.schedules[0].lessons[0].lesson_topic}\n"
                    else:
                        payload += "<em>No topic</em>\n"
                else:
                    payload += "Lessons not found\n"

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=payload,
                    parse_mode=enums.ParseMode.HTML,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)
            old_wd = wd

        msg = await self._send_close_message_sch_and_hw(
            sender, specific_day, homework_response
        )
        msg_ids.append(msg.id)
        await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

    @staticmethod
    async def to_homework_page(event: types.CallbackQuery):
        """
        Display `homework` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("For The Week", b"entire_homework")
                ], [
                    types.InlineKeyboardButton("For Tomorrow", b"tomorrows_homework"),
                ], [
                    types.InlineKeyboardButton("Specific Day »", b"specific_day_homework"),
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"main_page")
                ]
            ])
        )
        await event.answer()

    @staticmethod
    async def to_specific_day_homework_page(event: types.CallbackQuery):
        """
        Display `specific day homework` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            "Choose a day below         ↴",
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Monday", b"monday_homework"),
                    types.InlineKeyboardButton("Tuesday", b"tuesday_homework")
                ], [
                    types.InlineKeyboardButton("Wednesday", b"wednesday_homework"),
                    types.InlineKeyboardButton("Thursday", b"thursday_homework")
                ], [
                    types.InlineKeyboardButton("Friday", b"friday_homework"),
                    types.InlineKeyboardButton("Saturday", b"saturday_homework")
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"homework_page")
                ]
            ])
        )
        await event.answer()
