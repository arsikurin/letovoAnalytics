import asyncio
import datetime
import logging
import typing

import aiohttp
from pyrogram import Client, types, enums

from app.dependencies import (
    types as types_l, errors as errors_l, Web, Postgresql, Firestore, run_parallel
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
    __slots__ = ("_client", "__web", "__db", "__fs", "__payload")

    def __init__(
            self, client: Client, session: aiohttp.ClientSession, db: Postgresql, fs: Firestore
    ):
        self.client: Client = client
        self._web: Web = Web(session=session, fs=fs)
        self._db: Postgresql = db
        self._fs: Firestore = fs
        self._payload: str = ""

    @property
    def client(self) -> Client:
        return self._client

    @client.setter
    def client(self, value: Client):
        self._client = value

    @property
    def _web(self) -> Web:
        return self.__web

    @_web.setter
    def _web(self, value: Web):
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

    async def send_greeting(self, sender: types.User) -> types.Message:
        """
        Send a greeting to the end user

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        payload = f'{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}'.strip()
        return await self.client.send_message(
            chat_id=sender.id,
            text=f"Greetings, **{payload}**!",
            reply_markup=types.ReplyKeyboardMarkup([[
                types.KeyboardButton("Options")
            ]], resize_keyboard=True)
        )

    # async def send_start_page(self, sender: types.User) -> types.Message:
    #     return await self.client.send_message(
    #         chat_id=sender.id,
    #         text="I will help you access s.letovo.ru resources via Telegram.\n"
    #                 "  Initially, you should provide your **school** credentials.\n"
    #                 "  To do that click the **Log In** button below\n\n"
    #                 "__After logging into your account, click **Options** button__",
    #         reply_markup=types.ReplyKeyboardMarkup([
    #             Button.url(text="Click here to log in", url=f"{settings().URL_LOGIN_LOCAL}?sender_id={sender.id}")
    #         ]
    #     )

    async def send_help_page(self, sender: types.User) -> types.Message:
        """
        Send help page

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        return await self.client.send_message(
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
                 "**/options » Others » Letovo Diploma** — get Letovo Diploma progress\n"
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
            reply_markup=types.ReplyKeyboardMarkup([[
                types.KeyboardButton(
                    text="Click here to register",
                    web_app=types.WebAppInfo(url="https://letovo-analytics.web.app/webview")
                )
            ]], resize_keyboard=True),
            # reply_markup=types.InlineKeyboardMarkup([[
            #     types.InlineKeyboardButton(text="Click here to register",
            #                                url=f"{settings().URL_LOGIN_LOCAL}?sender_id={sender.id}")
            # ]]),
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

    async def send_common_page(self, sender: types.User) -> types.Message:
        """
        Send `small help` page

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        return await self.client.send_message(
            chat_id=sender.id,
            text="**What you can do:**\n"
                 "\n"
                 "• Enter **/options** or click the **Options** button below\n"
                 "• Enter **/help** to view the manual",
            reply_markup=types.ReplyKeyboardMarkup([
                [
                    types.KeyboardButton("Options")
                ]
            ], resize_keyboard=True)
        )

    async def send_main_page(self, sender: types.User) -> types.Message:
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
            response = await self._handle_errors(self._web.receive_marks_and_teachers, event, sender)
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
            # if int(datetime.datetime.now(tz=settings().timezone).strftime("%w")) == 0:
            return await event.answer("Congrats! It's Sunday, no lessons", show_alert=False)

        sender: types.User = event.from_user
        try:
            response = await self._handle_errors(self._web.receive_schedule_and_hw, event, sender, specific_day)
        except errors_l.StopPropagation:
            return
        schedule_response = ScheduleAndHWResponse.parse_obj(response)
        old_wd = ""
        msg_ids = []
        for day in schedule_response.data:
            if day.schedules and specific_day.value in {int(day.period_num_day), -10}:
                wd = types_l.Weekdays(int(day.period_num_day)).name
                if specific_day == types_l.Weekdays.ALL and wd != old_wd:
                    msg = await self.client.send_message(
                        chat_id=sender.id,
                        text=f"\n**=={wd}==**\n",
                        disable_notification=True
                    )
                    msg_ids.append(msg.id)

                payload = f"{day.period_name} | <em>{day.schedules[0].room.room_name}</em>:"
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
                msg = await self.client.send_message(
                    chat_id=sender.id,
                    text=payload,
                    parse_mode=enums.ParseMode.HTML,
                    disable_notification=True,
                    disable_web_page_preview=True
                )
                msg_ids.append(msg.id)
                old_wd = wd

        if specific_day != types_l.Weekdays.ALL:
            start_of_week = datetime.datetime.fromisoformat(schedule_response.data[0].date)
            msg = await self.client.send_message(
                chat_id=sender.id,
                text=f'__{specific_day.name}, '
                     f'{start_of_week.strftime("%d.%m.%Y")}__\n',
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton("Close", b"close")
                ]]),
                disable_notification=True
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
            response = await self._handle_errors(self._web.receive_marks_and_teachers, event, sender)
        except errors_l.StopPropagation:
            return
        homework_response = ScheduleAndHWResponse.parse_obj(response)
        old_wd = ""
        msg_ids = []
        for day in homework_response.data:
            if day.schedules and specific_day.value in {int(day.period_num_day), -10}:
                flag = False
                wd = types_l.Weekdays(int(day.period_num_day)).name
                if specific_day == types_l.Weekdays.ALL and wd != old_wd:
                    msg = await self.client.send_message(
                        chat_id=sender.id,
                        text=f"\n**=={wd}==**\n",
                        disable_notification=True
                    )
                    msg_ids.append(msg.id)

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

        if specific_day != types_l.Weekdays.ALL:
            start_of_week = datetime.datetime.fromisoformat(homework_response.data[0].date)
            msg = await self.client.send_message(
                chat_id=sender.id,
                text=f'__{specific_day.name}, '
                     f'{start_of_week.strftime("%d.%m.%Y")}__\n',
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton("Close", b"close")
                ]]),
                disable_notification=True
            )
            msg_ids.append(msg.id)
            await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

        await event.answer("Homework might not be displayed properly as it is in beta")

    async def _prepare_summative_marks(self, subject: MarksDataList, *, check_date: bool = False):
        """
        Parse summative marks

        Args:
            subject (MarksDataList): school subject
            check_date (bool): check for recency or not
        """
        mark_a, mark_b, mark_c, mark_d = [0, 0], [0, 0], [0, 0], [0, 0]
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

        mark_a_avg, mark_b_avg = f"{(mark_a[0] / mark_a[1]):.2g}", f"{(mark_b[0] / mark_b[1]):.2g}"
        mark_c_avg, mark_d_avg = f"{(mark_c[0] / mark_c[1]):.2g}", f"{(mark_d[0] / mark_d[1]):.2g}"

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

    async def _send_summative_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send summative marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            if subject.summative_list:
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"
                await self._prepare_summative_marks(subject)

                await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True
                )

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
                # TODO subject name not only eng should be
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"

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

                await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )

    async def _send_recent_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send recent marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            flag = False
            self._payload = f"**{subject.group.subject.subject_name_eng}**\n"

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
                await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )

    async def _send_all_marks(self, _marks_response: MarksResponse, sender: types.User):
        """
        Send all marks to the end user

        Args:
            _marks_response (MarksResponse): marks
            sender (types.User): end user
        """
        for subject in _marks_response.data:
            self._payload = f"**{subject.group.subject.subject_name_eng}**\n"

            if subject.formative_list:
                for mark in subject.formative_list:
                    self._payload += f"**{mark.mark_value}**F "

            if subject.summative_list:
                await self._prepare_summative_marks(subject)

            if subject.summative_list or subject.formative_list:
                await self.client.send_message(
                    chat_id=sender.id,
                    text=self._payload,
                    disable_notification=True,
                    disable_web_page_preview=True
                )

    async def _handle_errors(
            self, func: typing.Callable[[...], typing.Coroutine[typing.Any, typing.Any, dict]],
            event: types.CallbackQuery, sender: types.User,
            specific_day: types_l.Weekdays | None = None
    ) -> dict:
        """
        Boilerplate for error handling of `self._web.receive_marks_and_teachers` and `self._web.receive_schedule_and_hw`
        """
        if func == self._web.receive_marks_and_teachers:
            try:
                resp = await self._web.receive_marks_and_teachers(str(sender.id))
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

        elif func == self._web.receive_schedule_and_hw:
            if specific_day is None:
                logging.critical("Specific day value not provided!")
                raise errors_l.StopPropagation

            try:
                if specific_day != types_l.Weekdays.ALL:
                    resp = await self._web.receive_schedule_and_hw(
                        sender_id=str(sender.id), specific_day=specific_day, week=False
                    )
                else:
                    resp = await self._web.receive_schedule_and_hw(
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

    async def send_marks(
            self, event: types.CallbackQuery, specific: types_l.MarkTypes
    ):
        """
        Send marks to the end user

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
            specific (types_l.MarkTypes): ALL, SUMMATIVE, FINAL, RECENT
        """
        sender: types.User = event.from_user
        try:
            response = await self._handle_errors(self._web.receive_marks_and_teachers, event, sender)
        except errors_l.StopPropagation:
            return
        marks_response = MarksResponse.parse_obj(response)

        match specific:  # TODO test required
            case types_l.MarkTypes.SUMMATIVE:
                await self._send_summative_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.FINAL:
                await self._send_final_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.RECENT:
                await self._send_recent_marks(_marks_response=marks_response, sender=sender)
            case types_l.MarkTypes.ALL:
                await self._send_all_marks(_marks_response=marks_response, sender=sender)

        # if specific == types_l.MarkTypes.SUMMATIVE:
        #     await self._send_summative_marks(_marks_response=marks_response, sender=sender)
        # elif specific == types_l.MarkTypes.FINAL:
        #     await self._send_final_marks(_marks_response=marks_response, sender=sender)
        # elif specific == types_l.MarkTypes.RECENT:
        #     await self._send_recent_marks(_marks_response=marks_response, sender=sender)
        # elif specific == types_l.MarkTypes.ALL:
        #     await self._send_all_marks(_marks_response=marks_response, sender=sender)

        del self._payload
        await event.answer()


class CallbackQueryEventEditors(CallbackQuerySenders):
    """
    Class for dealing with callback query events
    """

    @staticmethod
    async def to_main_page(event: types.CallbackQuery):
        """
        Display `main` page

        Args:
            event (types.CallbackQuery): a return object of CallbackQuery
        """
        # TODO rename `main` page to `landing` page
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
                    types.InlineKeyboardButton("Letovo Diploma", b"diploma"),
                ], [
                    types.InlineKeyboardButton("Holidays", b"holidays"),
                ], [
                    types.InlineKeyboardButton(back_btn_text, b"main_page")
                ]
            ])
        )

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
