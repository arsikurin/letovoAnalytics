#!/usr/bin/python3.10

import asyncio
import requests as rq

from requests_futures.sessions import FuturesSession
from telethon import Button, events
from constants import LOGIN_URL_LOCAL, EPS
from classes.enums import Weekdays, MarkTypes
from classes.pydantic_models import MarksResponse, ScheduleResponse
from classes.errors import NothingFoundError, UnauthorizedError
from classes.web import Web


class CallbackQueryEventEditors:
    """
    Class for working with callback query events
    """

    @staticmethod
    async def to_main_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose an option below ↴",
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
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire schedule", b"entire_schedule")
                ], [
                    Button.inline("For Today", b"today_schedule"),
                ], [
                    Button.inline("Specific day »", b"specific_day_schedule"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_homework_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire homework", b"entire_homework")
                ], [
                    Button.inline("For Tomorrow", b"tomorrows_homework"),
                ], [
                    Button.inline("Specific day »", b"specific_day_homework"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_marks_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("All marks", b"all_marks")
                ], [
                    Button.inline("For Summatives", b"summative_marks"),
                ], [
                    Button.inline("Recent marks", b"recent_marks"),
                ], [
                    Button.inline("« Back", b"main_page")
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
                    Button.inline("« Back", b"schedule_page")
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
                    Button.inline("« Back", b"homework_page")
                ]
            ]
        )


class CallbackQuerySenders:
    __slots__ = ("client",)

    def __init__(self, c):
        self.client = c

    async def send_greeting(self, sender):
        payload = f'{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}'.strip()
        await self.client.send_message(
            entity=sender,
            message=f'Greetings, **{payload}**!',
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ], [
                    Button.text("Clear previous", resize=True, single_use=False)
                ]
            ]
        )

    async def send_start(self, sender):
        await asyncio.sleep(0.05)
        await self.client.send_message(
            entity=sender,
            message="I will help you access s.letovo.ru resources via Telegram.\n"
                    "  Initially, you should provide your **school** credentials.\n"
                    "  To do that click the **Log In** button below\n\n"
                    "__After logging into your account, click **Options** button__",
            parse_mode="md",
            buttons=[
                Button.url(text="Click here to log in", url=f'{LOGIN_URL_LOCAL}?chat_id={sender.id}')
            ]
        )

    async def send_about(self, sender):
        await asyncio.sleep(0.05)
        await self.client.send_message(
            entity=sender,
            message="**Arseny Kurin**\n\n"
                    "• 2024kurin.av@student.letovo.ru\n"
                    "• [Github](https://github.com/arsikurin)\n"
                    "• [Telegram](https://t.me/arsikurin)\n",
            parse_mode="md"
        )

    async def send_help(self, sender):
        await asyncio.sleep(0.05)
        await self.client.send_message(
            entity=sender,
            message="**Marks:**\n"
                    "__0-8__A — summative A\n"
                    "__0-8__B — summative B\n"
                    "__0-8__C — summative C\n"
                    "__0-8__D — summative D\n"
                    "__0-8__F — formative",
            parse_mode="md"
        )

    async def send_main_page(self, sender):
        await self.client.send_message(
            entity=sender,
            message="Choose an option below ↴",
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

    async def send_holidays(self, sender):
        # TODO receive holidays from API
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
            self, s: FuturesSession, event: events.CallbackQuery.Event, specific_day: Weekdays
    ):
        """
        parse and send specific day(s) from schedule

        :param event: a return object of CallbackQuery
        :param s: requests_futures session
        :param specific_day: day number or -10 to send entire schedule
        """
        schedule_future = await Web.receive_hw_n_schedule(s, str(event.sender_id))
        if schedule_future == UnauthorizedError:
            return await event.answer("[✘] Cannot get data from s.letovo.ru", alert=True)

        if schedule_future == NothingFoundError:
            return await event.answer(
                "[✘] Nothing found in database for this user.\nPlease enter /start and register",
                alert=True
            )

        if schedule_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)

        if specific_day == Weekdays.Sunday2:
            return await event.answer("Congrats! It's Sunday, no lessons", alert=False)

        old_wd = 0
        schedule_response = ScheduleResponse.parse_obj(schedule_future.result().json())
        if specific_day.value != -10:
            date = schedule_response.data[0].date.split("-")
            await self.client.send_message(
                entity=await event.get_sender(),
                message=f'__{specific_day.name}, {int(date[2]) + specific_day.value - 1}.{date[1]}.{date[0]}__\n',
                parse_mode="md",
                silent=True
            )

        for day in schedule_response.data:

            if day.schedules and specific_day.value in (int(day.period_num_day), -10):
                wd = Weekdays(int(day.period_num_day)).name
                if specific_day.value == -10 and wd != old_wd:
                    await self.client.send_message(
                        entity=await event.get_sender(),
                        message=f'\n**=={wd}==**\n',
                        parse_mode="md",
                        silent=True
                    )

                payload = f'{day.period_name} | __{day.schedules[0].room.room_name}__:'
                if day.schedules[0].lessons[0].attendance:
                    payload += "  [ Missed ]\n"
                else:
                    payload += "\n"
                payload += f'**{day.schedules[0].group.subject.subject_name_eng} ' \
                           f'{day.schedules[0].group.group_name}**\n'

                payload += f'{day.period_start} — {day.period_end}\n'
                if day.schedules[0].zoom_meetings:
                    payload += f'[ZOOM]({day.schedules[0].zoom_meetings.meeting_url})'
                await self.client.send_message(
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
                )
                old_wd = wd
        await event.answer()

    async def send_homework(
            self, s: FuturesSession, event: events.CallbackQuery.Event, specific_day: Weekdays
    ):
        """
        parse and send specific day(s) from homework

        :param event: a return object of CallbackQuery
        :param s: requests_futures session
        :param specific_day: day number or -10 to send all homework
        """
        homework_future = await Web.receive_hw_n_schedule(s, str(event.sender_id))
        if specific_day == Weekdays.Sunday:
            return await event.answer("Congrats! Tomorrow's Sunday, no hw", alert=False)

        if homework_future == UnauthorizedError:
            return await event.answer("[✘] Cannot get data from s.letovo.ru", alert=True)

        if homework_future == NothingFoundError:
            return await event.answer(
                "[✘] Nothing found in database for this user.\nPlease type /start and register",
                alert=True
            )

        if homework_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)

        for day in homework_future.result().json()["data"]:
            if len(day["schedules"]) > 0 and specific_day.value in (int(day["period_num_day"]), -10):
                ch = False
                payload = (
                    f'{day["period_name"]}: <strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} '
                    f'{day["schedules"][0]["group"]["group_name"]}</strong>\n'
                    f'{Weekdays(int(day["period_num_day"])).name}, {day["date"]}\n'
                )

                if day["schedules"][0]["lessons"][0]["lesson_hw"]:
                    payload += f'{day["schedules"][0]["lessons"][0]["lesson_hw"]}\n'
                else:
                    payload += "<em>No homework</em>\n"

                if day["schedules"][0]["lessons"][0]["lesson_url"]:
                    ch = True
                    payload += f'<a href="{day["schedules"][0]["lessons"][0]["lesson_url"]}">Attached link</a>\n'

                if day["schedules"][0]["lessons"][0]["lesson_hw_url"]:
                    ch = True
                    payload += f'<a href="{day["schedules"][0]["lessons"][0]["lesson_hw_url"]}">Attached hw link</a>\n'

                if not ch:
                    payload += "<em>No links attached</em>\n"

                if day["schedules"][0]["lessons"][0]["lesson_thema"]:
                    payload += f'{day["schedules"][0]["lessons"][0]["lesson_thema"]}\n'
                else:
                    payload += "<em>No topic</em>\n"

                await self.client.send_message(
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="html",
                    silent=True
                )
        await event.answer()

    async def send_marks(
            self, s: FuturesSession, event: events.CallbackQuery.Event, specific: MarkTypes
    ):
        """
        parse and send marks

        :param event: a return object of CallbackQuery
        :param s: requests_futures session
        :param specific: all, sum, recent
        """
        marks_future = await Web.receive_marks(s, str(event.sender_id))
        if marks_future == UnauthorizedError:
            return await event.answer("[✘] Cannot get data from s.letovo.ru", alert=True)

        if marks_future == NothingFoundError:
            return await event.answer(
                "[✘] Nothing found in database for this user.\nPlease enter /start and register",
                alert=True
            )

        if marks_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)

        # TODO recent marks
        marks_response = MarksResponse.parse_obj(marks_future.result().json())
        for subject in marks_response.data:
            if specific == MarkTypes.Only_summative and subject.summative_list:
                payload = f"**{subject.group.subject.subject_name_eng}**\n"

                marks = [(mark.mark_value, mark.mark_criterion) for mark in subject.summative_list]
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
                    payload += f"**{mark[0]}**{mark[1]} "

                if mark_a[1] == 0:
                    mark_a[1] = 1
                if mark_b[1] == 0:
                    mark_b[1] = 1
                if mark_c[1] == 0:
                    mark_c[1] = 1
                if mark_d[1] == 0:
                    mark_d[1] = 1

                mark_a_avg, mark_b_avg = mark_a[0] / mark_a[1], mark_b[0] / mark_b[1]
                mark_c_avg, mark_d_avg = mark_c[0] / mark_c[1], mark_d[0] / mark_d[1]
                if abs(mark_a_avg % 1) < EPS:
                    mark_a_avg = round(mark_a_avg)
                if abs(mark_b_avg % 1) < EPS:
                    mark_b_avg = round(mark_b_avg)
                if abs(mark_c_avg % 1) < EPS:
                    mark_c_avg = round(mark_c_avg)
                if abs(mark_d_avg % 1) < EPS:
                    mark_d_avg = round(mark_d_avg)
                payload += f" | __avg:__ **{mark_a_avg}**A **{mark_b_avg}**B **{mark_c_avg}**C **{mark_d_avg}**D"
                await self.client.send_message(
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="md",
                    silent=True
                )

            elif specific == MarkTypes.ALL:
                payload = f"**{subject.group.subject.subject_name_eng}**\n "
                if subject.formative_list:
                    for mark in subject.formative_list:
                        payload += f"**{mark.mark_value}**F "

                if subject.summative_list:
                    marks = [(mark.mark_value, mark.mark_criterion) for mark in subject.summative_list]
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
                        payload += f"**{mark[0]}**{mark[1]} "

                    if mark_a[1] == 0:
                        mark_a[1] = 1
                    if mark_b[1] == 0:
                        mark_b[1] = 1
                    if mark_c[1] == 0:
                        mark_c[1] = 1
                    if mark_d[1] == 0:
                        mark_d[1] = 1

                    mark_a_avg, mark_b_avg = mark_a[0] / mark_a[1], mark_b[0] / mark_b[1]
                    mark_c_avg, mark_d_avg = mark_c[0] / mark_c[1], mark_d[0] / mark_d[1]
                    if abs(mark_a_avg % 1) < EPS:
                        mark_a_avg = round(mark_a_avg)
                    if abs(mark_b_avg % 1) < EPS:
                        mark_b_avg = round(mark_b_avg)
                    if abs(mark_c_avg % 1) < EPS:
                        mark_c_avg = round(mark_c_avg)
                    if abs(mark_d_avg % 1) < EPS:
                        mark_d_avg = round(mark_d_avg)
                    payload += f" | __AVG:__ **{mark_a_avg}**A **{mark_b_avg}**B **{mark_c_avg}**C **{mark_d_avg}**D"
                if subject.summative_list or subject.formative_list:
                    await self.client.send_message(
                        entity=await event.get_sender(),
                        message=payload,
                        parse_mode="md",
                        silent=True
                    )
        await event.answer()


class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    """
    Class for working with callback query
    """
