#  Made by arsikurin in 2022.

import datetime

from pyrogram import types

from app.bot.callbackquery.base import CBQueryBase
from app.dependencies import errors as errors_l, types as types_l
from app.schemas import MarksResponse, MarksDataList
from config import settings

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQMarks(CBQueryBase):
    async def send_marks(
            self, event: types.CallbackQuery, specific: types_l.MarkTypes
    ):
        """
        Send marks to the end user

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
            specific (types_l.MarkTypes): SUMMATIVE, FINAL, RECENT, ALL
        """

        sender: types.User = event.from_user
        try:
            response = await self._handle_errors(self._api.receive_marks_and_teachers, event, sender)
        except errors_l.StopPropagation:
            return
        marks_response = MarksResponse.parse_obj(response)

        match specific:
            case types_l.MarkTypes.SUMMATIVE:
                await self._send_summative_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.FINAL:
                await self._send_final_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.RECENT:
                await self._send_recent_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.ALL:
                await self._send_all_marks(_marks_response=marks_response, sender=sender)

        if self._msg_ids:
            msg = await self._send_close_message_marks(sender, specific)
            self._msg_ids.append(msg.id)
            await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, self._msg_ids)))

        del self._payload
        del self._msg_ids
        await event.answer()

    async def _send_summative_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send summative marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            if subject.summative_list:
                if subject.group.subject.subject_name_eng:
                    subject_name = subject.group.subject.subject_name_eng
                else:
                    subject_name = subject.group.subject.subject_name
                self._payload = f"**{subject_name}**\n"
                await self._prepare_summative_marks(subject)

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True
                )
                self._msg_ids.append(msg.id)

    async def _prepare_summative_marks(self, subject: MarksDataList, *, check_date: bool = False):
        """
        Parse summative marks

        Args:
            subject (MarksDataList): school subject
            check_date (bool): check for recency or not
        """
        mark_a, mark_b, mark_c, mark_d, mark_s = [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]
        for mark in subject.summative_list:
            if mark.mark_value.isdigit():
                if mark.mark_criterion == "A":
                    mark_a[0] += int(mark.mark_value)
                    mark_a[1] += 1
                elif mark.mark_criterion == "B":
                    mark_b[0] += int(mark.mark_value)
                    mark_b[1] += 1
                elif mark.mark_criterion == "C":
                    mark_c[0] += int(mark.mark_value)
                    mark_c[1] += 1
                elif mark.mark_criterion == "D":
                    mark_d[0] += int(mark.mark_value)
                    mark_d[1] += 1
                elif mark.mark_criterion == "S":
                    mark_s[0] += int(mark.mark_value)
                    mark_s[1] += 1
            if not check_date or (
                    datetime.datetime.now(tz=settings().timezone) -
                    datetime.datetime.fromisoformat(mark.created_at).replace(tzinfo=settings().timezone)
            ).days < 8:
                self._payload += f"**{mark.mark_value}**{mark.mark_criterion} "

        if mark_a[1] == 0:
            mark_a[1] = 1
        if mark_b[1] == 0:
            mark_b[1] = 1
        if mark_c[1] == 0:
            mark_c[1] = 1
        if mark_d[1] == 0:
            mark_d[1] = 1
        if mark_s[1] == 0:
            mark_s[1] = 1

        mark_a_avg, mark_b_avg = f"{(mark_a[0] / mark_a[1]):.2g}", f"{(mark_b[0] / mark_b[1]):.2g}"
        mark_c_avg, mark_d_avg = f"{(mark_c[0] / mark_c[1]):.2g}", f"{(mark_d[0] / mark_d[1]):.2g}"
        mark_s_avg = f"{(mark_s[0] / mark_s[1]):.2g}"

        if self._payload[-2] == "*":
            self._payload += "no recent marks"

        self._payload += " | __avg:__ "
        if float(mark_a_avg) > 0:
            self._payload += f"**{mark_a_avg}**A "
        if float(mark_b_avg) > 0:
            self._payload += f"**{mark_b_avg}**B "
        if float(mark_c_avg) > 0:
            self._payload += f"**{mark_c_avg}**C "
        if float(mark_d_avg) > 0:
            self._payload += f"**{mark_d_avg}**D "
        if float(mark_s_avg) > 0:
            self._payload += f"**{mark_s_avg}**S "

    async def _send_final_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send final marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            if subject.final_mark_list:
                year_mark = None
                if subject.group.subject.subject_name_eng:
                    subject_name = subject.group.subject.subject_name_eng
                else:
                    subject_name = subject.group.subject.subject_name
                self._payload = f"**{subject_name}**\n"

                # TODO sort final marks
                if isinstance(subject.final_mark_list, list):
                    for mark in subject.final_mark_list:
                        self._payload += f"**{mark.final_value}**{mark.final_criterion} "
                else:
                    for mark in subject.final_mark_list.values():
                        if mark["final_criterion"] != "Y":
                            self._payload += f"**{mark['final_value']}**{mark['final_criterion']} "
                        else:
                            year_mark = mark["final_value"]

                if subject.group_avg_mark:
                    self._payload += f" | __group_avg:__ **{subject.group_avg_mark}**"

                if subject.result_final_mark:
                    self._payload += f" | __semester:__ **{subject.result_final_mark}**"

                if year_mark is not None:
                    self._payload += f" | __year:__ **{year_mark}**"

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                self._msg_ids.append(msg.id)

    async def _send_recent_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send recent marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            flag = False
            if subject.group.subject.subject_name_eng:
                subject_name = subject.group.subject.subject_name_eng
            else:
                subject_name = subject.group.subject.subject_name
            self._payload = f"**{subject_name}**\n"

            if subject.formative_list:
                for mark in subject.formative_list:
                    created_at = datetime.datetime.fromisoformat(mark.created_at)
                    now = datetime.datetime.now(tz=settings().timezone)
                    if (now - created_at.replace(tzinfo=settings().timezone)).days < 8:
                        flag = True
                        self._payload += f"**{mark.mark_value}**F "

            if subject.summative_list:
                await self._prepare_summative_marks(subject, check_date=True)

            if flag or subject.summative_list:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                self._msg_ids.append(msg.id)

    async def _send_all_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send all marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            if subject.group.subject.subject_name_eng:
                subject_name = subject.group.subject.subject_name_eng
            else:
                subject_name = subject.group.subject.subject_name
            self._payload = f"**{subject_name}**\n"

            if subject.formative_list:
                for mark in subject.formative_list:
                    self._payload += f"**{mark.mark_value}**F "

            if subject.summative_list:
                await self._prepare_summative_marks(subject)

            if subject.summative_list or subject.formative_list:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                self._msg_ids.append(msg.id)

    @staticmethod
    async def to_marks_page(event: types.CallbackQuery):
        """
        Display `marks` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        await event.edit_message_text(
            choose_an_option_below_text,
            reply_markup=types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("All marks", b"all_marks")
                ], [
                    types.InlineKeyboardButton("Recent marks", b"recent_marks"),
                ], [
                    types.InlineKeyboardButton("Summatives", b"summative_marks"),
                    types.InlineKeyboardButton("Finals", b"final_marks"),
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"main_page")
                ]
            ])
        )
        await event.answer()
