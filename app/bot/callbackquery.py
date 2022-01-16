import asyncio
import datetime
import typing

import aiohttp
from telethon import Button, events, TelegramClient, types

from app.dependencies import (
    types as types_l, errors as errors_l, Web, AnalyticsDatabase, CredentialsDatabase
)
from app.schemas import MarksResponse, MarksDataList, ScheduleResponse, HomeworkResponse
from config import settings

choose_an_option_below = "Choose an option below ↴"
back = "« Back"


class CallbackQueryEventEditors:
    """
    Class for working with callback query events
    """

    @staticmethod
    async def to_main_page(event: events.CallbackQuery.Event):
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
                    Button.inline("Holidays", b"holidays"),
                ]
            ]
        )

    @staticmethod
    async def to_schedule_page(event: events.CallbackQuery.Event):
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire schedule", b"entire_schedule")
                ], [
                    Button.inline("For Today", b"today_schedule"),
                ], [
                    Button.inline("Specific day »", b"specific_day_schedule"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_homework_page(event: events.CallbackQuery.Event):
        await event.edit(
            choose_an_option_below,
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire homework", b"entire_homework")
                ], [
                    Button.inline("For Tomorrow", b"tomorrows_homework"),
                ], [
                    Button.inline("Specific day »", b"specific_day_homework"),
                ], [
                    Button.inline(back, b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_marks_page(event: events.CallbackQuery.Event):
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
    async def to_specific_day_schedule_page(event: events.CallbackQuery.Event):
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
    __slots__ = ("_client", "__web", "__db", "__fs", "__payload")

    def __init__(
            self, client: TelegramClient, session: aiohttp.ClientSession, db: AnalyticsDatabase, fs: CredentialsDatabase
    ):
        self.client: TelegramClient = client
        self._web: Web = Web(session)
        self._db: AnalyticsDatabase = db
        self._fs: CredentialsDatabase = fs
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
    def _db(self) -> AnalyticsDatabase:
        return self.__db

    @_db.setter
    def _db(self, value: AnalyticsDatabase):
        self.__db = value

    @property
    def _fs(self) -> CredentialsDatabase:
        return self.__fs

    @_fs.setter
    def _fs(self, value: CredentialsDatabase):
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

    async def send_greeting(self, sender: types.User):
        payload = f'{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}'.strip()
        await self.client.send_message(
            entity=sender,
            message=f"Greetings, **{payload}**!",
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ]
            ]
        )

    async def send_start_page(self, sender: types.User):
        await self.client.send_message(
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

    async def send_help_page(self, sender: types.User):
        await self.client.send_message(
            entity=sender,
            message="I can help you access s.letovo.ru resources via Telegram.\n"
                    "If you're new here, please see the [Terms of Use](https://example.com) and "
                    "provide your **school** credentials, i. e. login and password,"
                    " **__(Button below the message)__** to begin enjoying the service\n"
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
                    "**/options » schedule » __day__** — get schedule\n"
                    "**/options » marks** — get marks\n"
                    "**/options » homework » __day__ ** — get homework **[beta]**\n"
                    "\n"
                    "\n"
                    "**Bot Settings**\n"
                    "__coming soon__\n"
                    "\n"
                    "\n"
                    "**Marks CI**\n"
                    "From **0** to **8** following by a criterion:\n"
                    "**A**, **B**, **C** or **D** — Summative marks\n"
                    "**F** — Formative marks\n"
                    "\n"
                    "__For example:__\n"
                    "• **7A** means **7** for Summative **A**\n"
                    "• **5B** means **5** for Summative **B**\n"
                    "• **6F** means **6** for Formative\n",
            buttons=[
                Button.url(text="Click here to log in", url=f"{settings().URL_LOGIN_LOCAL}?sender_id={sender.id}")
            ],
            parse_mode="md",
            link_preview=False
        )

    async def send_stats_page(self, sender: types.User):
        for user in await self._db.get_users():
            resp = await self._db.get_analytics(user)
            if not any((
                    resp.schedule_counter, resp.homework_counter, resp.marks_counter, resp.holidays_counter,
                    resp.options_counter, resp.help_counter, resp.about_counter
            )): continue  # noqa

            name, surname, login = await asyncio.gather(
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

    async def send_about_page(self, sender: types.User):
        await self.client.send_message(
            entity=sender,
            message="**Arseny Kurin**\n\n"
                    "• 2024kurin.av@student.letovo.ru\n"
                    "• [Github](https://github.com/arsikurin)\n"
                    "• [Telegram](https://t.me/arsikurin)\n",
            parse_mode="md"
        )

    async def send_main_page(self, sender: types.User):
        await self.client.send_message(
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
                    Button.inline("Holidays", b"holidays"),
                ]
            ]
        )

    async def send_dev_page(self, sender: types.User):
        await self.client.send_message(
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
        # TODO receive holidays from API

        sender: types.User = await event.get_sender()
        await self.client.send_message(
            entity=sender,
            message="__after__ **unit I**\n31.10.2021 — 07.11.2021",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit II**\n26.12.2021 — 09.01.2022",
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

    async def send_schedule(
            self, event: events.CallbackQuery.Event, specific_day: types_l.Weekdays
    ):
        """
        parse & send specific day(s) from schedule

        :param event: a return object of CallbackQuery
        :param specific_day: day of the week represented by Weekdays enum
        """
        if specific_day == types_l.Weekdays.Sunday:
            return await event.answer("Congrats! It's Sunday, no lessons", alert=False)
        sender: types.User = await event.get_sender()
        try:
            schedule_resp = await self._web.receive_hw_n_schedule(sender_id=str(sender.id), fs=self._fs)
        except errors_l.UnauthorizedError as err:
            return await event.answer(f"[✘] {err}", alert=True)
        except errors_l.NothingFoundError as err:
            # "[✘] Nothing found in database for this user.\nPlease enter /start and register"
            return await event.answer(f"[✘] {err}", alert=True)
        except aiohttp.ClientConnectionError as err:
            return await event.answer(f"[✘] {err}", alert=True)

        old_wd = 0
        schedule_response = ScheduleResponse.parse_raw(schedule_resp)
        if specific_day.value != -10:
            date = schedule_response.data[0].date.split("-")
            await self.client.send_message(
                entity=sender,
                message=f"__{specific_day.name}, {int(date[2]) + specific_day.value - 1}.{date[1]}.{date[0]}__\n",
                parse_mode="md",
                silent=True
            )

        for day in schedule_response.data:
            if day.schedules and specific_day.value in (int(day.period_num_day), -10):
                wd = types_l.Weekdays(int(day.period_num_day)).name
                if specific_day.value == -10 and wd != old_wd:
                    await self.client.send_message(
                        entity=sender,
                        message=f"\n**=={wd}==**\n",
                        parse_mode="md",
                        silent=True
                    )

                payload = f"{day.period_name} | __{day.schedules[0].room.room_name}__:\n"
                # if day.schedules[0].lessons[0].attendance:
                #     payload += "  Missed\n"
                # else:
                #     payload += "\n"
                if day.schedules[0].group.subject.subject_name_eng:
                    subject = day.schedules[0].group.subject.subject_name_eng
                else:
                    subject = day.schedules[0].group.subject.subject_name
                payload += f"**{subject} {day.schedules[0].group.group_name}**\n"

                payload += f"{day.period_start} — {day.period_end}\n"
                if day.schedules[0].zoom_meetings:
                    payload += f"[ZOOM]({day.schedules[0].zoom_meetings.meeting_url})"
                await self.client.send_message(
                    entity=sender,
                    message=payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
                )
                old_wd = wd
        await event.answer()

    async def send_homework(
            self, event: events.CallbackQuery.Event, specific_day: types_l.Weekdays
    ):
        """
        parse & send specific day(s) from homework

        :param event: a return object of CallbackQuery
        :param specific_day: day of the week represented by Weekdays enum
        """

        if specific_day == types_l.Weekdays.SundayHW:
            return await event.answer("Congrats! Tomorrow's Sunday, no hw", alert=False)
        sender: types.User = await event.get_sender()
        try:
            homework_resp = await self._web.receive_hw_n_schedule(sender_id=str(sender.id), fs=self._fs)
        except errors_l.UnauthorizedError as err:
            return await event.answer(f"[✘] {err}", alert=True)
        except errors_l.NothingFoundError as err:
            # "[✘] Nothing found in database for this user.\nPlease enter /start and register"
            return await event.answer(f"[✘] {err}", alert=True)
        except aiohttp.ClientConnectionError as err:
            return await event.answer(f"[✘] {err}", alert=True)

        homework_response = HomeworkResponse.parse_raw(homework_resp)
        for day in homework_response.data:
            if day.schedules and specific_day.value in (int(day.period_num_day), -10):
                flag = False
                payload = (
                    f'{day.period_name}: <strong>{day.schedules[0].group.subject.subject_name_eng} '
                    f'{day.schedules[0].group.group_name}</strong>\n'
                    f'{types_l.Weekdays(int(day.period_num_day)).name}, {day.date}\n'
                )
                if day.schedules[0].lessons:
                    if day.schedules[0].lessons[0].lesson_hw:
                        payload += f'{day.schedules[0].lessons[0].lesson_hw}\n'
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
                        payload += f'{day.schedules[0].lessons[0].lesson_topic}\n'
                    else:
                        payload += "<em>No topic</em>\n"
                else:
                    payload += "Lessons not found\n"

                await self.client.send_message(
                    entity=sender,
                    message=payload,
                    parse_mode="html",
                    silent=True,
                    link_preview=False
                )
        await event.answer()

    async def _prepare_summative_marks(self, subject: MarksDataList, check_date: bool = False):
        """
        Parse summative marks
        """
        marks = [(mark.mark_value, mark.mark_criterion, mark.created_at) for mark in subject.summative_list]

        mark_a, mark_b, mark_c, mark_d = [0, 0], [0, 0], [0, 0], [0, 0]
        for mark in marks:
            if mark[1] == "A" and mark[0].isdigit():
                mark_a[0] += int(mark[0])
                mark_a[1] += 1
            elif mark[1] == "B" and mark[0].isdigit():
                mark_b[0] += int(mark[0])
                mark_b[1] += 1
            elif mark[1] == "C" and mark[0].isdigit():
                mark_c[0] += int(mark[0])
                mark_c[1] += 1
            elif mark[1] == "D" and mark[0].isdigit():
                mark_d[0] += int(mark[0])
                mark_d[1] += 1
            if not check_date or (datetime.datetime.today() - datetime.datetime.fromisoformat(mark[2])).days < 7:
                self._payload += f"**{mark[0]}**{mark[1]} "

        if mark_a[1] == 0:  # refactor
            mark_a[1] = 1
        if mark_b[1] == 0:
            mark_b[1] = 1
        if mark_c[1] == 0:
            mark_c[1] = 1
        if mark_d[1] == 0:
            mark_d[1] = 1

        mark_a_avg, mark_b_avg = mark_a[0] / mark_a[1], mark_b[0] / mark_b[1]
        mark_c_avg, mark_d_avg = mark_c[0] / mark_c[1], mark_d[0] / mark_d[1]

        round_mark = lambda avg: round(avg) if abs(avg % 1) < settings().EPS else round(avg, 1)
        mark_a_avg = round_mark(mark_a_avg)
        mark_b_avg = round_mark(mark_b_avg)
        mark_c_avg = round_mark(mark_c_avg)
        mark_d_avg = round_mark(mark_d_avg)

        if self._payload[-2] == "*":
            self._payload += "no recent marks"

        self._payload += f" | __avg:__ "
        if mark_a_avg > 0:
            self._payload += f"**{mark_a_avg}**A "
        if mark_b_avg > 0:
            self._payload += f"**{mark_b_avg}**B "
        if mark_c_avg > 0:
            self._payload += f"**{mark_c_avg}**C "
        if mark_d_avg > 0:
            self._payload += f"**{mark_d_avg}**D "

    async def send_marks(
            self, event: events.CallbackQuery.Event, specific: types_l.MarkTypes
    ):
        """
        parse & send marks

        :param event: a return object of CallbackQuery
        :param specific: all, sum, recent
        """
        sender: types.User = await event.get_sender()
        try:
            marks_resp = await self._web.receive_marks(sender_id=str(sender.id), fs=self._fs)
        except errors_l.UnauthorizedError as err:
            return await event.answer(f"[✘] {err}", alert=True)
        except errors_l.NothingFoundError as err:
            # "[✘] Nothing found in database for this user.\nPlease enter /start and register"
            return await event.answer(f"[✘] {err}", alert=True)
        except aiohttp.ClientConnectionError as err:
            return await event.answer(f"[✘] {err}", alert=True)

        # TODO recent marks
        marks_response = MarksResponse.parse_raw(marks_resp)
        for subject in marks_response.data:
            if specific == types_l.MarkTypes.SUMMATIVE and subject.summative_list:
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"
                await self._prepare_summative_marks(subject)
                await self.client.send_message(
                    entity=sender,
                    message=self._payload,
                    parse_mode="md",
                    silent=True
                )

            elif specific == types_l.MarkTypes.FINAL:
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"
                if subject.final_mark_list:
                    for mark in subject.final_mark_list:
                        self._payload += f"**{mark.final_value}**{mark.final_criterion} "
                    if subject.result_final_mark:
                        self._payload += f" | __final:__ **{subject.result_final_mark}**"

                    if subject.group_avg_mark:
                        self._payload += f" | __group:__ **{subject.group_avg_mark}**"
                    await self.client.send_message(
                        entity=sender,
                        message=self._payload,
                        parse_mode="md",
                        silent=True,
                        link_preview=False
                    )

            elif specific == types_l.MarkTypes.RECENT:
                self._payload = f"**{subject.group.subject.subject_name_eng}**\n"
                if subject.formative_list:
                    for mark in subject.formative_list:
                        created_at = datetime.datetime.fromisoformat(mark.created_at)
                        if (datetime.datetime.today() - created_at).days < 7:
                            self._payload += f"**{mark.mark_value}**F "

                if subject.summative_list:
                    await self._prepare_summative_marks(subject, check_date=True)

                if subject.summative_list or subject.formative_list:
                    await self.client.send_message(
                        entity=sender,
                        message=self._payload,
                        parse_mode="md",
                        silent=True,
                        link_preview=False
                    )

            elif specific == types_l.MarkTypes.ALL:
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
        del self._payload
        await event.answer()


@typing.final
class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    """
    Class for working with callback query
    """
