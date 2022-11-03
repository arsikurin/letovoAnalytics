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
        msg_ids = []

        match specific:
            case types_l.MarkTypes.SUMMATIVE:
                await self._send_summative_marks(sender=sender, _marks_response=marks_response, msg_ids=msg_ids)
            case types_l.MarkTypes.FINAL:
                await self._send_final_marks(sender=sender, _marks_response=marks_response, msg_ids=msg_ids)
            case types_l.MarkTypes.RECENT:
                await self._send_recent_marks(sender=sender, _marks_response=marks_response, msg_ids=msg_ids)
            case types_l.MarkTypes.ALL:
                await self._send_all_marks(sender=sender, _marks_response=marks_response, msg_ids=msg_ids)

        if msg_ids:
            msg = await self._send_close_message_marks(sender, specific)
            msg_ids.append(msg.id)
            await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

        await event.answer()

    async def _send_summative_marks(self, sender: types.User, _marks_response: MarksResponse, msg_ids: list[int]):
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
                payload = [f"**{subject_name}**\n"]

                await self._prepare_summative_marks(payload, subject)

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text="".join(payload),
                    disable_notification=True
                )
                msg_ids.append(msg.id)

    @staticmethod
    async def _prepare_summative_marks(payload: list[str], subject: MarksDataList, *, check_date: bool = False):
        """
        Parse summative marks

        Args:
            subject (MarksDataList): school subject
            check_date (bool): check for recency or not
        """
        mark_a, mark_b, mark_c = types_l.Mark(criterion="A"), types_l.Mark(criterion="B"), types_l.Mark(criterion="C")
        mark_d, mark_s = types_l.Mark(criterion="D"), types_l.Mark(criterion="S")

        for mark in subject.summative_list:
            if mark.mark_value.isdigit():
                if mark.mark_criterion == "A":
                    mark_a.sum += int(mark.mark_value)
                    mark_a.count += 1

                elif mark.mark_criterion == "B":
                    mark_b.sum += int(mark.mark_value)
                    mark_b.count += 1

                elif mark.mark_criterion == "C":
                    mark_c.sum += int(mark.mark_value)
                    mark_c.count += 1

                elif mark.mark_criterion == "D":
                    mark_d.sum += int(mark.mark_value)
                    mark_d.count += 1

                elif mark.mark_criterion == "S":
                    mark_s.sum += int(mark.mark_value)
                    mark_s.count += 1

            if not check_date or (
                    datetime.datetime.now(tz=settings().timezone) -
                    datetime.datetime.fromisoformat(mark.created_at).replace(tzinfo=settings().timezone)
            ).days < 8:
                payload.append(f"**{mark.mark_value}**{mark.mark_criterion} ")

        if payload[-1][-2] == "*":
            payload.append("no recent marks")

        def _add_avg_mark_if_exists(_mark: types_l.Mark):
            """
            This is a private helper for '_prepare_summative_marks',
            used to verify the presence of mark in journal and if true calculate its average value,
            then append to payload list
            """
            nonlocal payload
            if _mark.count != 0:
                mark_avg = _mark.sum / _mark.count
                payload.append(f"**{mark_avg:.2g}**{_mark.criterion} ")

        payload.append(" | __avg:__ ")
        _add_avg_mark_if_exists(mark_a)
        _add_avg_mark_if_exists(mark_b)
        _add_avg_mark_if_exists(mark_c)
        _add_avg_mark_if_exists(mark_d)
        _add_avg_mark_if_exists(mark_s)

    async def _send_final_marks(self, sender: types.User, _marks_response: MarksResponse, msg_ids: list[int]):
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
                payload = [f"**{subject_name}**\n"]

                # TODO sort final marks
                if isinstance(subject.final_mark_list, list):
                    for mark in subject.final_mark_list:
                        payload.append(f"**{mark.final_value}**{mark.final_criterion} ")
                else:
                    for mark in subject.final_mark_list.values():
                        if mark["final_criterion"] != "Y":
                            payload.append(f"**{mark['final_value']}**{mark['final_criterion']} ")
                        else:
                            year_mark = mark["final_value"]

                if subject.group_avg_mark:
                    payload.append(f" | __group_avg:__ **{subject.group_avg_mark}**")

                if subject.result_final_mark:
                    payload.append(f" | __semester:__ **{subject.result_final_mark}**")

                if year_mark is not None:
                    payload.append(f" | __year:__ **{year_mark}**")

                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text="".join(payload),
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)

    async def _send_recent_marks(self, sender: types.User, _marks_response: MarksResponse, msg_ids: list[int]):
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
            payload = [f"**{subject_name}**\n"]

            if subject.formative_list:
                for mark in subject.formative_list:
                    created_at = datetime.datetime.fromisoformat(mark.created_at)
                    now = datetime.datetime.now(tz=settings().timezone)
                    if (now - created_at.replace(tzinfo=settings().timezone)).days < 8:
                        flag = True
                        payload.append(f"**{mark.mark_value}**F ")

            if subject.summative_list:
                await self._prepare_summative_marks(payload, subject, check_date=True)

            if flag or subject.summative_list:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text="".join(payload),
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)

    async def _send_all_marks(self, sender: types.User, _marks_response: MarksResponse, msg_ids: list[int]):
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
            payload = [f"**{subject_name}**\n"]

            if subject.formative_list:
                for mark in subject.formative_list:
                    payload.append(f"**{mark.mark_value}**F ")

            if subject.summative_list:
                await self._prepare_summative_marks(payload, subject)

            if subject.summative_list or subject.formative_list:
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text="".join(payload),
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)

    async def _send_close_message_marks(self, sender: types.User, specific: types_l.MarkTypes):
        now = datetime.datetime.now(tz=settings().timezone)

        if specific == types_l.MarkTypes.RECENT:
            payload = (
                f"__{specific.name.capitalize()} marks, "
                f"{(now - datetime.timedelta(7)):%d.%m.%Y} — {now:%d.%m.%Y}__\n"
            )
        elif specific == types_l.MarkTypes.FINAL:
            payload = (
                f"__{specific.name.capitalize()} marks, semester__\n"
            )
        else:
            payload = (
                f"__{specific.name.capitalize()} marks, {now:%d.%m.%Y}__\n"
            )

        return await self.client.send_message(
            chat_id=sender.id,
            text=payload,
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton("Close", b"close")
            ]]),
            disable_notification=True
        )

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
