import datetime
import typing

import aiohttp
from telethon import Button, events, TelegramClient, types

from app.dependencies import (
    types as types_l, errors as errors_l, Web, Postgresql, Firestore, run_parallel
)
from app.schemas import MarksResponse, MarksDataList, ScheduleResponse, HomeworkResponse, TeachersResponse
from config import settings

choose_an_option_below = "Choose an option below ↴"
back = "« Back"


class CallbackQueryEventEditors:
    """
    Class for working with callback query events
    """

    @staticmethod
    async def to_main_page(event: events.CallbackQuery.Event):
        """
        Display `main` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        # TODO rename `main` page to `landing` page
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Schedule »", b"schedule_page")
                ], [
                    Button.inline("Homework »", b"homework_page"),
                ], [
                    Button.inline("Marks »", b"marks_page"),
                ], [
                    Button.inline("Others »", b"others_page"),
                ]
            ]
        )

    @staticmethod
    async def to_schedule_page(event: events.CallbackQuery.Event):
        """
        Display `schedule` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("For The Week", b"entire_schedule")
                ], [
                    Button.inline("For Today", b"today_schedule"),
                ], [
                    Button.inline("Specific Day »", b"specific_day_schedule"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_homework_page(event: events.CallbackQuery.Event):
        """
        Display `homework` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("For The Week", b"entire_homework")
                ], [
                    Button.inline("For Tomorrow", b"tomorrows_homework"),
                ], [
                    Button.inline("Specific Day »", b"specific_day_homework"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_marks_page(event: events.CallbackQuery.Event):
        """
        Display `marks` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("All marks", b"all_marks")
                ], [
                    Button.inline("Recent marks", b"recent_marks"),
                ], [
                    Button.inline("Summatives", b"summative_marks"),
                    Button.inline("Finals", b"final_marks"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_others_page(event: events.CallbackQuery.Event):
        """
        Display `others` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Teachers' info", b"teachers")
                ], [
                    Button.inline("Letovo Diploma", b"diploma"),
                ], [
                    Button.inline("Holidays", b"holidays"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_schedule_page(event: events.CallbackQuery.Event):
        """
        Display `specific day schedule` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            "Choose a day below         ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_schedule"),
                    Button.inline("Tuesday", b"tuesday_schedule")
                ], [
                    Button.inline("Wednesday", b"wednesday_schedule"),
                    Button.inline("Thursday", b"thursday_schedule")
                ], [
                    Button.inline("Friday", b"friday_schedule"),
                    Button.inline("Saturday", b"saturday_schedule")
                ], [
                    Button.inline(back, b"schedule_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_homework_page(event: events.CallbackQuery.Event):
        """
        Display `specific day homework` page

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        await event.edit(
            "Choose a day below         ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_homework"),
                    Button.inline("Tuesday", b"tuesday_homework")
                ], [
                    Button.inline("Wednesday", b"wednesday_homework"),
                    Button.inline("Thursday", b"thursday_homework")
                ], [
                    Button.inline("Friday", b"friday_homework"),
                    Button.inline("Saturday", b"saturday_homework")
                ], [
                    Button.inline(back, b"homework_page")
                ]
            ]
        )


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
            self, client: TelegramClient, session: aiohttp.ClientSession, db: Postgresql, fs: Firestore
    ):
        self.client: TelegramClient = client
        self._web: Web = Web(session=session, fs=fs)
        self._db: Postgresql = db
        self._fs: Firestore = fs
        self._payload: str = ""

    @property
    def client(self) -> TelegramClient:
        return self._client

    @client.setter
    def client(self, value: TelegramClient):
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
            entity=sender,
            message=f"Greetings, **{payload}**!",
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ]
            ]
        )

    async def send_start_page(self, sender: types.User) -> types.Message:
        return await self.client.send_message(
            entity=sender,
            message="I will help you access s.letovo.ru resources via Telegram.\n"
                    "  Initially, you should provide your **school** credentials.\n"
                    "  To do that click the **Log In** button below\n\n"
                    "__After logging into your account, click **Options** button__",
            parse_mode="md",
            buttons=[
                Button.url(text="Click here to log in", url=f"{settings().URL_LOGIN_LOCAL}?sender_id={sender.id}")
            ]
        )

    async def send_help_page(self, sender: types.User) -> types.Message:
        """
        Send help page

        Args:
            sender (types.User): end user

        Returns:
            types.Message
        """
        return await self.client.send_message(
            entity=sender,
            message="I can help you access s.letovo.ru resources via Telegram.\n"
                    "If you're new here, please see the [Terms of Use](https://example.com) and "
                    "provide your **school** credentials, i.e. login and password,"
                    " to begin enjoying the service.\n"
                    "To do this, click the **button below the message**.\n"
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
                    "From **0** to **8** following by a criterion:\n"  # todo
                    "**A**, **B**, **C** or **D** — Summative marks\n"
                    "**F** — Formative marks\n"
                    "\n"
                    "__For example:__\n"
                    "• **7A** means **7** for Summative **A**\n"
                    "• **5B** means **5** for Summative **B**\n"
                    "• **6F** means **6** for Formative\n",
            buttons=[
                Button.url(text="Click here to register", url=f"{settings().URL_LOGIN_LOCAL}?sender_id={sender.id}")
            ],
            parse_mode="md",
            link_preview=False
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
            )): continue  # noqa

            name, surname, login = await run_parallel(
                self._fs.get_name(resp.sender_id),
                self._fs.get_surname(resp.sender_id),
                self._fs.get_login(resp.sender_id),
            )
            name = name if name is not errors_l.NothingFoundError else ""
            surname = surname if surname is not errors_l.NothingFoundError else ""
            login = login if login is not errors_l.NothingFoundError else ""
            await self.client.send_message(
                entity=sender,
                message=f"ID: {resp.sender_id}\n"
                        f"Name: {name} {surname}\n"
                        f"Login: {login}\n"
                        f"Schedule: {resp.schedule_counter}\n"
                        f"Homework {resp.homework_counter}\n"
                        f"Marks: {resp.marks_counter}\n"
                        f"Holidays: {resp.holidays_counter}\n"
                        f"Options: {resp.options_counter}\n"
                        f"Help: {resp.help_counter}\n"
                        f"About: {resp.about_counter}",
                parse_mode="md"
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
            entity=sender,
            message="**Arseny Kurin**\n\n"
                    "• 2024kurin.av@student.letovo.ru\n"
                    "• [Github](https://github.com/arsikurin)\n"
                    "• [Telegram](https://t.me/arsikurin)\n",
            parse_mode="md"
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
            entity=sender,
            message="**What you can do:**\n"
                    "\n"
                    "• Enter **/options** or click the **Options** button below\n"
                    "• Enter **/help** to view the manual",
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ]
            ]
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
            entity=sender,
            message=choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Schedule »", b"schedule_page")
                ], [
                    Button.inline("Homework »", b"homework_page"),
                ], [
                    Button.inline("Marks »", b"marks_page"),
                ], [
                    Button.inline("Others »", b"others_page"),
                ]
            ]
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
            entity=sender,
            message=choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Statistics", b"stats")
                ], [
                    Button.inline("Update tokens", b"tokens"),
                ]
            ]
        )

    async def send_holidays(self, event: events.CallbackQuery.Event):
        """
        Send holidays

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        # TODO receive holidays from API
        sender: types.User = await event.get_sender()
        await self.client.send_message(
            entity=sender,
            message="__after__ **unit I**\n31.10.2021 — 07.11.2021",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit II**\n26.12.2021 — 12.01.2022",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit III**\n13.03.2022 — 20.03.2022",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit IV**\n22.05.2022 — 31.08.2022",
            parse_mode="md"
        )
        await event.answer()

    async def send_teachers(
            self, event: events.CallbackQuery.Event
    ):
        """
        Parse & send teachers' names

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
        """
        sender: types.User = await event.get_sender()
        try:
            teachers_resp = await self._web.receive_marks_and_teachers(sender_id=str(sender.id))
        except errors_l.UnauthorizedError as err:
            return await event.answer(f"[✘] {err}", alert=True)
        except errors_l.NothingFoundError as err:
            return await event.answer(f"[✘] {err}", alert=True)
        except aiohttp.ClientConnectionError as err:
            return await event.answer(f"[✘] {err}", alert=True)

        teachers_response = TeachersResponse.parse_obj(teachers_resp)
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
                    entity=sender,
                    message=payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
                )
        await event.answer()

    async def send_schedule(
            self, event: events.CallbackQuery.Event, specific_day: types_l.Weekdays
    ):
        """
        Parse & send schedule

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
            specific_day (types_l.Weekdays): day of the week
        """
        if specific_day == types_l.Weekdays.TODAY and \
                int(datetime.datetime.now(tz=settings().timezone).strftime("%w")) == 0:
            return await event.answer("Congrats! It's Sunday, no lessons", alert=False)

        sender: types.User = await event.get_sender()
        try:
            if specific_day == types_l.Weekdays.TODAY:
                schedule_resp = await self._web.receive_schedule_and_hw(
                    sender_id=str(sender.id), week=False
                )
            else:
                schedule_resp = await self._web.receive_schedule_and_hw(
                    sender_id=str(sender.id)
                )
        except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
            return await event.answer(f"[✘] {err}", alert=True)

        old_wd = ""
        msg_ids = []
        schedule_response = ScheduleResponse.parse_obj(schedule_resp)
        for day in schedule_response.data:
            if day.schedules and specific_day.value in {int(day.period_num_day), -10, -15}:
                wd = types_l.Weekdays(int(day.period_num_day)).name
                if specific_day == types_l.Weekdays.ALL and wd != old_wd:
                    msg = await self.client.send_message(
                        entity=sender,
                        message=f"\n**=={wd}==**\n",
                        parse_mode="md",
                        silent=True
                    )
                    msg_ids.append(msg.id)

                payload = f"{day.period_name} | <em>{day.schedules[0].room.room_name}</em>:\n"
                # if day.schedules[0].lessons[0].attendance:
                #     payload += "  Missed\n"
                # else:
                #     payload += "\n"
                if day.schedules[0].group.subject.subject_name_eng:
                    subject = day.schedules[0].group.subject.subject_name_eng
                else:
                    subject = day.schedules[0].group.subject.subject_name
                payload += f"<strong>{subject} {day.schedules[0].group.group_name}</strong>\n"

                payload += f"{day.period_start} — {day.period_end}\n"
                if day.schedules[0].zoom_meetings:
                    payload += f"<a href='{day.schedules[0].zoom_meetings.meeting_url}'>ZOOM</a>"
                msg = await self.client.send_message(
                    entity=sender,
                    message=payload,
                    parse_mode="html",
                    silent=True,
                    link_preview=False
                )
                msg_ids.append(msg.id)
                old_wd = wd

        if specific_day != types_l.Weekdays.ALL:
            if specific_day == types_l.Weekdays.TODAY:
                today = datetime.datetime.now(tz=settings().timezone).strftime("%A")
            else:
                today = specific_day.name
            start_of_week = datetime.datetime.fromisoformat(schedule_response.data[0].date)
            msg = await self.client.send_message(
                entity=sender,
                message=f'__{today}, '
                        f'{(start_of_week + datetime.timedelta(specific_day.value - 1)).strftime("%d.%m.%Y")}__\n',
                buttons=[
                    Button.inline("Close", b"close")
                ],
                parse_mode="md",
                silent=True
            )
            msg_ids.append(msg.id)
            await self._db.set_msg_ids(sender_id=str(sender.id), msg_ids=" ".join(map(str, msg_ids)))

        await event.answer()

    async def send_homework(
            self, event: events.CallbackQuery.Event, specific_day: types_l.Weekdays
    ):
        """
        Parse & send homework

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
            specific_day (types_l.Weekdays): day of the week
        """
        if specific_day == types_l.Weekdays.SundayHW:
            return await event.answer("Congrats! Tomorrow's Sunday, no hw", alert=False)

        sender: types.User = await event.get_sender()
        try:
            homework_resp = await self._web.receive_schedule_and_hw(sender_id=str(sender.id))
        except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
            return await event.answer(f"[✘] {err}", alert=True)

        old_wd = ""
        homework_response = HomeworkResponse.parse_obj(homework_resp)
        msg_ids = []
        for day in homework_response.data:
            if day.schedules and specific_day.value in {int(day.period_num_day), -10}:
                flag = False
                wd = types_l.Weekdays(int(day.period_num_day)).name
                if specific_day == types_l.Weekdays.ALL and wd != old_wd:
                    msg = await self.client.send_message(
                        entity=sender,
                        message=f"\n**=={wd}==**\n",
                        parse_mode="md",
                        silent=True
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
                    entity=sender,
                    message=payload,
                    parse_mode="html",
                    silent=True,
                    link_preview=False
                )
                msg_ids.append(msg.id)

                old_wd = wd

        if specific_day != types_l.Weekdays.ALL:
            start_of_week = datetime.datetime.fromisoformat(homework_response.data[0].date)
            msg = await self.client.send_message(
                entity=sender,
                message=f'__{specific_day.name}, '
                        f'{(start_of_week + datetime.timedelta(specific_day.value - 1)).strftime("%d.%m.%Y")}__\n',
                buttons=[
                    Button.inline("Close", b"close")
                ],
                parse_mode="md",
                silent=True
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
                    entity=sender,
                    message=self._payload,
                    parse_mode="md",
                    silent=True
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
                # TODO subject name not only eng should be
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"

                # TODO sort final marks
                for mark in subject.final_mark_list:
                    self._payload += f"**{mark.final_value}**{mark.final_criterion} "

                if subject.group_avg_mark:
                    self._payload += f" | __group_avg:__ **{subject.group_avg_mark}**"

                if subject.result_final_mark:
                    self._payload += f" | __final:__ **{subject.result_final_mark}**"

                await self.client.send_message(
                    entity=sender,
                    message=self._payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
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
                    entity=sender,
                    message=self._payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
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
                    entity=sender,
                    message=self._payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
                )

    async def send_marks(
            self, event: events.CallbackQuery.Event, specific: types_l.MarkTypes
    ):
        """
        Send marks to the end user

        Args:
            event (events.CallbackQuery.Event): a return object of CallbackQuery
            specific (types_l.MarkTypes): ALL, SUMMATIVE, FINAL, RECENT
        """
        sender: types.User = await event.get_sender()
        try:
            marks_resp = await self._web.receive_marks_and_teachers(sender_id=str(sender.id))
        except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
            return await event.answer(f"[✘] {err}", alert=True)

        marks_response = MarksResponse.parse_obj(marks_resp)
        if specific == types_l.MarkTypes.SUMMATIVE:
            await self._send_summative_marks(_marks_response=marks_response, sender=sender)
        elif specific == types_l.MarkTypes.FINAL:
            await self._send_final_marks(_marks_response=marks_response, sender=sender)
        elif specific == types_l.MarkTypes.RECENT:
            await self._send_recent_marks(_marks_response=marks_response, sender=sender)
        elif specific == types_l.MarkTypes.ALL:
            await self._send_all_marks(_marks_response=marks_response, sender=sender)

        del self._payload
        await event.answer()


@typing.final
class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    """
    Class for dealing with callback query
    """
