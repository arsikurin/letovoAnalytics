#  Made by arsikurin in 2022.

from pyrogram import types, enums

from app.bot.callbackquery.base import CBQueryBase
from app.dependencies import errors as errors_l, types as types_l
from app.schemas import ScheduleAndHWResponse

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQSchedule(CBQueryBase):
    async def send_schedule(
            self, event: types.CallbackQuery, specific_day: types_l.Weekdays
    ):
        """
        Parse & send schedule

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
            specific_day (types_l.Weekdays): day of the week
        """
        if specific_day == types_l.Weekdays.Sunday:
            return await event.answer("Congrats! It's Sunday, no lessons", show_alert=False)

        sender: types.User = event.from_user
        try:
            response = await self._handle_errors(self._api.receive_schedule_and_hw, event, sender, specific_day)
        except errors_l.StopPropagation:
            return

        schedule_response = ScheduleAndHWResponse.parse_obj(response)
        old_wd = ""
        msg_ids = []
        for day in schedule_response.data:
            wd = types_l.Weekdays(int(day.period_num_day)).name
            if specific_day == types_l.Weekdays.Week and wd != old_wd:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=f"\n==={wd}===\n",
                    disable_notification=True
                )
                msg_ids.append(msg.id)

            payload = ""
            if day.schedules:
                payload += f"{day.period_name} | <em>{day.schedules[0].room.room_name}</em>:"

                if day.schedules[0].lessons and day.schedules[0].lessons[0].attendance:
                    payload += "  Ditched\n"
                else:
                    payload += "\n"
                if day.schedules[0].group.subject.subject_name_eng:
                    subject = day.schedules[0].group.subject.subject_name_eng
                else:
                    subject = day.schedules[0].group.subject.subject_name
                payload += f"<strong>{subject} {day.schedules[0].group.group_name}</strong>\n"

                payload += f"{day.period_start} — {day.period_end}\n"
                if day.schedules[0].zoom_meetings:
                    payload += f"<a href='{day.schedules[0].zoom_meetings.meeting_url}'>ZOOM</a>"

            elif day.period_start == "08:25":
                payload += f"{day.period_name}:\n"
                payload += f"{day.period_start} — {day.period_end}\n"

            old_wd = wd

            if payload != "":
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=payload,
                    parse_mode=enums.ParseMode.HTML,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)

        msg = await self._send_close_message_sch_and_hw(
            sender, specific_day, schedule_response
        )
        msg_ids.append(msg.id)
        await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

        await event.answer()

    @staticmethod
    async def to_schedule_page(event: types.CallbackQuery):
        """
        Display `schedule` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("For The Week", b"entire_schedule")
                ], [
                    types.InlineKeyboardButton("For Today", b"today_schedule"),
                ], [
                    types.InlineKeyboardButton("Specific Day »", b"specific_day_schedule"),
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"main_page")
                ]
            ])
        )
        await event.answer()

    @staticmethod
    async def to_specific_day_schedule_page(event: types.CallbackQuery):
        """
        Display `specific day schedule` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            "Choose a day below         ↴",
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("Monday", b"monday_schedule"),
                    types.InlineKeyboardButton("Tuesday", b"tuesday_schedule")
                ], [
                    types.InlineKeyboardButton("Wednesday", b"wednesday_schedule"),
                    types.InlineKeyboardButton("Thursday", b"thursday_schedule")
                ], [
                    types.InlineKeyboardButton("Friday", b"friday_schedule"),
                    types.InlineKeyboardButton("Saturday", b"saturday_schedule")
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"schedule_page")
                ]
            ])
        )
        await event.answer()
