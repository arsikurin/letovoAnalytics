import asyncio
import datetime
import logging
import typing
from io import BytesIO

import aiohttp
from ics import Calendar
from pyrogram import Client, types, enums

from app.dependencies import (
    types as types_l, errors as errors_l, API, Postgresql, Firestore, run_parallel
)
from app.schemas import MarksResponse, MarksDataList, ScheduleAndHWResponse, TeachersResponse
from config import settings

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CallbackQuerySenders:
    """
    Class for dealing with callback query messages

    Args:
        session (aiohttp.ClientSession): an instance of `TelegramClient` with credentials filled in
        session (aiohttp.ClientSession): an instance of `aiohttp.ClientSession`
        db (Postgresql): connection to the database with users' usage analytics
        fs (Firestore): connection to the database with users' credentials
    """
    __slots__ = ("_client", "__web", "__db", "__fs", "__payload", "__msg_ids")

    def __init__(
            self, client: Client, session: aiohttp.ClientSession, db: Postgresql, fs: Firestore
    ):
        self.client: Client = client
        self._api: API = API(session=session, fs=fs)
        self._db: Postgresql = db
        self._fs: Firestore = fs
        self._payload = ""
        self._msg_ids = []

    @property
    def client(self) -> Client:
        return self._client

    @client.setter
    def client(self, value: Client):
        self._client = value

    @property
    def _api(self) -> API:
        return self.__web

    @_api.setter
    def _api(self, value: API):
        self.__web = value

    @property
    def _db(self) -> Postgresql:
        return self.__db

    @_db.setter
    def _db(self, value: Postgresql):
        self.__db = value

    @property
    def _fs(self) -> Firestore:
        return self.__fs

    @_fs.setter
    def _fs(self, value: Firestore):
        self.__fs = value

    @property
    def _payload(self) -> str:
        return self.__payload

    @_payload.setter
    def _payload(self, value: str):
        self.__payload = value

    @_payload.deleter
    def _payload(self):
        self.__payload = ""

    @property
    def _msg_ids(self) -> list:
        return self.__msg_ids

    @_msg_ids.setter
    def _msg_ids(self, value: list):
        self.__msg_ids = value

    @_msg_ids.deleter
    def _msg_ids(self):
        self.__msg_ids.clear()

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
                 "**/options » Others » Schedule to calendar (.ics)** — get .ics file with current week schedule\n"
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

            name, surname, login = await run_parallel(
                self._fs.get_name(resp.sender_id),
                self._fs.get_surname(resp.sender_id),
                self._fs.get_login(resp.sender_id),
            )
            name = name if name is not errors_l.NothingFoundError else ""
            surname = surname if surname is not errors_l.NothingFoundError else ""
            login = login if login is not errors_l.NothingFoundError else ""
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

    # async def send_settings_page(self, sender: types.User) -> types.Message:
    #     """
    #     Send settings page
    #
    #     Args:
    #         sender (types.User): end user
    #
    #     Returns:
    #         types.Message
    #     """
    #     main_email = ""
    #     spare_emails = [
    #         "", ""
    #     ]
    #     buttons = [
    #         [
    #             types.InlineKeyboardButton(main_email, b"set_1"),
    #             types.InlineKeyboardButton("Active", b"set_1"),
    #             types.InlineKeyboardButton("Remove", b"remove_1")
    #         ]
    #     ]
    #     for i, email in enumerate(spare_emails):
    #         buttons.append(
    #             [
    #                 types.InlineKeyboardButton(email, f"set_{i + 2}"),
    #                 types.InlineKeyboardButton("Remove", f"remove_{i + 2}"),
    #             ]
    #         )
    #     if len(spare_emails) < 2:
    #         buttons.append(
    #             [
    #                 Button.url("Add", settings().URL_LOGIN_LOCAL),
    #             ]
    #         )
    #
    #     return await self.client.send_message(
    #         chat_id=sender.id,
    #         text="Settings",
    #         reply_markup=types.ReplyKeyboardMarkup(buttons
    #     )

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

    async def send_schedule_ics(
            self, event: types.CallbackQuery
    ):
        """
        Parse & send schedule .ics file

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        sender: types.User = event.from_user
        try:
            response = await self._api.receive_schedule_ics(sender_id=str(sender.id))
        except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
            await event.answer(f"[✘] {err}", show_alert=True)
            return
        except asyncio.TimeoutError as err:
            await self.client.send_message(
                chat_id=sender.id,
                text=f"[✘] {err.__str__()}",
                disable_notification=True,
                disable_web_page_preview=True
            )
            return

        c = Calendar(response.decode())
        for lesson in c.timeline:
            lesson.name = lesson.name.split("(")[0].split(":")[-1].strip()

            description = lesson.description.split(";")[0].split("(")[0].strip()
            link = lesson.description.split(";")[-1].split(":")[-1].strip()
            if link == "no link":
                description += f"\nZoom: {link}"
            lesson.description = description

        file = BytesIO(c.serialize().encode())
        file.name = "schedule.ics"
        await self.client.send_document(sender.id, file)
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
        teachers_response = TeachersResponse.parse_obj(response)
        for subject in teachers_response.data:
            if subject.group.group_teachers:
                if subject.group.subject.subject_name_eng:
                    subject_name = subject.group.subject.subject_name_eng
                else:
                    subject_name = subject.group.subject.subject_name
                payload = f"**{subject_name} {subject.group.group_name}**\n"

                for subject_teacher in subject.group.group_teachers:
                    t = subject_teacher.teacher
                    payload += f"{t.teacher_name} {t.teacher_fath} {t.teacher_surname}\n{t.teacher_mail}\n\n"

                await self.client.send_message(
                    chat_id=sender.id,
                    text=payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
        await event.answer()

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
                if day.schedules[0].lessons[0].attendance:
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

    async def _send_close_message_sch_and_hw(
            self, sender: types.User, specific_day: types_l.Weekdays, schedule_response: ScheduleAndHWResponse
    ) -> types.Message:
        date_of_lessons = datetime.datetime.fromisoformat(schedule_response.data[0].date)
        if specific_day == types_l.Weekdays.Week:
            payload = (
                f"__{specific_day.name}, "
                f"{date_of_lessons:%d.%m.%Y} — {(date_of_lessons + datetime.timedelta(6)):%d.%m.%Y}__\n"
            )
        else:
            payload = (
                f"__{specific_day.name}, "
                f"{date_of_lessons:%d.%m.%Y}__\n"
            )
        return await self.client.send_message(
            chat_id=sender.id,
            text=payload,
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton("Close", b"close")
            ]]),
            disable_notification=True
        )

    async def send_marks(
            self, event: types.CallbackQuery, specific: types_l.MarkTypes
    ):
        """
        Send marks to the end user

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
            specific (types_l.MarkTypes): Week, SUMMATIVE, FINAL, RECENT
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

    async def _send_close_message_marks(self, sender: types.User, specific: types_l.MarkTypes.SUMMATIVE):
        now = datetime.datetime.now(tz=settings().timezone)
        if specific == types_l.MarkTypes.RECENT:
            payload = (
                f"__{specific.name.capitalize()} marks, "
                f"{(now - datetime.timedelta(7)) :%d.%m.%Y} — {now:%d.%m.%Y}__\n"
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

    async def _handle_errors(
            self, func: typing.Callable[[...], typing.Coroutine[typing.Any, typing.Any, dict]],
            event: types.CallbackQuery, sender: types.User,
            specific_day: types_l.Weekdays | None = None
    ) -> dict:
        """
        Boilerplate for error handling of
                         ``self._web.receive_marks_and_teachers`` and ``self._web.receive_schedule_and_hw``
        """
        if func == self._api.receive_marks_and_teachers:
            try:
                resp = await self._api.receive_marks_and_teachers(str(sender.id))
            except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
                await event.answer(f"[✘] {err}", show_alert=True)
                raise errors_l.StopPropagation
            except asyncio.TimeoutError as err:
                await self.client.send_message(
                    chat_id=sender.id,
                    text=f"[✘] {err.__str__()}",
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                raise errors_l.StopPropagation
            return resp

        elif func == self._api.receive_schedule_and_hw:
            if specific_day is None:
                logging.critical("Specific day value not provided!")
                raise errors_l.StopPropagation

            try:
                if specific_day != types_l.Weekdays.Week:
                    resp = await self._api.receive_schedule_and_hw(
                        sender_id=str(sender.id), specific_day=specific_day, week=False
                    )
                else:
                    resp = await self._api.receive_schedule_and_hw(
                        sender_id=str(sender.id), specific_day=specific_day
                    )
            except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
                await event.answer(f"[✘] {err}", show_alert=True)
                raise errors_l.StopPropagation
            except asyncio.TimeoutError as err:
                await self.client.send_message(
                    chat_id=sender.id,
                    text=f"[✘] {err.__str__()}",
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                raise errors_l.StopPropagation
            return resp


class CallbackQueryEventEditors(CallbackQuerySenders):
    """
    Class for dealing with callback query events
    """

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
                    types.InlineKeyboardButton("Schedule to calendar (.ics)", b"schedule_ics"),
                ], [
                    types.InlineKeyboardButton("Holidays", b"holidays"),
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

    # @staticmethod
    # async def set_account(event: types.CallbackQuery):
    #     sender: types.User = event.from_user
    #     to_active = int(event.data.split(b"_")[-1])
    #     buttons: types.ReplyInlineMarkup = (await event.get_message()).reply_markup
    #     choices = {1, 2, 3}
    #     choices.remove(to_active)
    #
    #     if len(buttons.rows[to_active - 1].buttons) == 3:
    #         await event.answer("Already in use!")
    #     else:
    #         choice = choices.pop()
    #         if len(buttons.rows[choice - 1].buttons) == 3:
    #             cur_active = choice - 1
    #         else:
    #             cur_active = choices.pop() - 1
    #         buttons.rows[cur_active].buttons.pop(1)
    #         buttons.rows[to_active - 1].buttons.insert(1, types.InlineKeyboardButton("Active", event.data))
    #         # TODO swap current active and future active accounts
    #         await event.edit_message_text(
    #             "settings",
    #             reply_markup=types.ReplyKeyboardMarkup(buttons
    #         )

    # @staticmethod
    # async def remove_account(event: types.CallbackQuery):
    #     sender: types.User = event.from_user
    #     to_remove = int(event.data.split(b"_")[-1])
    #     buttons: types.ReplyInlineMarkup = (await event.get_message()).reply_markup
    #
    #     if len(buttons.rows[to_remove - 1].buttons) == 3:
    #         await event.answer("Cannot remove address in use!")
    #     else:
    #         buttons.rows[to_remove - 1].buttons.clear()
    #         buttons.rows[to_remove - 1].buttons.append(Button.url("Add", settings().URL_LOGIN_LOCAL))
    #         # TODO remove account
    #         await event.edit_message_text(
    #             "settings",
    #             reply_markup=types.ReplyKeyboardMarkup(buttons
    #         )


@typing.final
class CallbackQuery(CallbackQueryEventEditors):
    """
    Class for dealing with callback query
    """
