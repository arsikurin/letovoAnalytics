#!/usr/bin/python3.10

import asyncio
import requests as rq

from requests_futures.sessions import FuturesSession
from telethon import Button, events
from constants import MAIN_URL_LETOVO, LOGIN_URL_LOCAL
from classes.enums import Weekdays, MarkTypes
from classes.pydantic_models import MarksResponse
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
                    Button.inline("For Today", b"todays_schedule"),
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
                    Button.inline("Only for Summatives", b"only_summative_marks"),
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
    def __init__(self, c):
        self.client = c

    async def send_greeting(self, sender):
        await self.client.send_message(
            entity=sender,
            message=f'Greetings, **{f if (f := sender.first_name) else ""} {l if (l := sender.last_name) else ""}**!',
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ], [
                    Button.text("Clear previous", resize=True, single_use=False)
                ]
            ]
        )

    async def send_init_message(self, sender):
        await asyncio.sleep(0.05)
        await self.client.send_message(
            entity=sender,
            message="I will help you access your schedule via Telegram.\n"
                    "Initially, you should provide your **login** and **password** to"
                    f" [Letovo Analytics]({MAIN_URL_LETOVO}).\n  "
                    f'To do that click the **Log In** button below\n\n'
                    "__After logging into your account, click Options button__",
            parse_mode="md",
            buttons=[
                Button.url(text="Click to log in", url=f'{LOGIN_URL_LOCAL}?chat_id={sender.id}')
            ]
        )

    async def send_about_message(self, sender):
        await asyncio.sleep(0.05)
        await self.client.send_message(
            entity=sender,
            message="**Arseny Kurin**\n\n"
                    "• 2024kurin.av@student.letovo.ru\n"
                    "• [Github](https://github.com/arsikurin)\n"
                    "• [Telegram](https://t.me/arsikurin)\n",
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

    async def send_specific_day_schedule(
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
        schedule = schedule_future.result().json()["data"]
        if specific_day.value != -10:
            date = schedule[0]["date"].split("-")
            await self.client.send_message(
                entity=await event.get_sender(),
                message=f'<em>{specific_day.name}, {int(date[2]) + specific_day.value - 1}.{date[1]}.{date[0]}</em>\n',
                parse_mode="html",
                silent=True
            )

        for day in schedule:
            if len(day["schedules"]) > 0 and specific_day.value in (int(day["period_num_day"]), -10):
                wd = Weekdays(int(day["period_num_day"])).name
                if specific_day.value == -10 and wd != old_wd:
                    await self.client.send_message(
                        entity=await event.get_sender(),
                        message=f'\n<strong>=={wd}==</strong>\n',
                        parse_mode="html",
                        silent=True
                    )

                payload = f'{day["period_name"]} | <em>{day["schedules"][0]["room"]["room_name"]}</em>:\n'
                payload += f'<strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} ' \
                           f'{day["schedules"][0]["group"]["group_name"]}</strong>\n'
                if day["schedules"][0]["zoom_meetings"]:
                    payload += f'[ZOOM]({day["schedules"][0]["zoom_meetings"][0]["meeting_url"]}\n)'
                payload += f'{day["period_start"]} — {day["period_end"]}\n'
                await self.client.send_message(
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="html",
                    silent=True
                )
                old_wd = wd
        await event.answer()

    async def send_specific_day_homework(
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
                "[✘] Nothing found in database for this user.\nPlease enter /start and register",
                alert=True
            )

        if homework_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)
        # TODO
        for day in homework_future.result().json()["data"]:
            if len(day["schedules"]) > 0 and specific_day.value in (int(day["period_num_day"]), -10):
                ch = False
                payload = f'{day["period_name"]}: <strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} {day["schedules"][0]["group"]["group_name"]}</strong>\n' + \
                          f'{Weekdays(int(day["period_num_day"])).name}, {day["date"]}\n'

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

        # TODO marks parsing
        marks_response = MarksResponse.parse_obj(marks_future.result().json())
        for subject in marks_response.data:
            if specific == MarkTypes.Only_summative and len(subject.summative_list) > 0:
                payload = f'**{subject.group.subject.subject_name_eng} {subject.group.group_name}**\n'

                marks = [(mark.mark_value, mark.mark_criterion) for mark in subject.summative_list]
                markA, markB, markC, markD = [0, 0], [0, 0], [0, 0], [0, 0]
                for mark in sorted(marks, key=lambda x: x[1]):
                    if mark[1] == "A":
                        markA[0] += int(mark[0])
                        markA[1] += 1
                    elif mark[1] == "B":
                        markB[0] += int(mark[0])
                        markB[1] += 1
                    elif mark[1] == "C":
                        markC[0] += int(mark[0])
                        markC[1] += 1
                    elif mark[1] == "D":
                        markD[0] += int(mark[0])
                        markD[1] += 1
                    payload += f"{mark[0]}**{mark[1]}**"

                if markA[1] == 0:
                    markA[1] = 1
                if markB[1] == 0:
                    markB[1] = 1
                if markC[1] == 0:
                    markC[1] = 1
                if markD[1] == 0:
                    markD[1] = 1
                payload += f" | __AVG:__ {markA[0] / markA[1]}**A** {markB[0] / markB[1]}**B** {markC[0] / markC[1]}**C** {markD[0] / markD[1]}**D**"

                # date = subject["date"].split("-")
                # payload += f'{Weekdays(int(subject["period_num_day"])).name}, {date[2]}.{date[1]}.{date[0]}\n'

                await self.client.send_message(
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="md",
                    silent=True
                )
            elif specific == MarkTypes.ALL:
                ch = False
                payload = f'**{subject.group.subject.subject_name_eng}**\n'
                if len(subject.formative_list) > 0:
                    ch = True
                    for mark in subject.formative_list:
                        payload += f'**{mark.mark_value}**F '

                if len(subject.summative_list) > 0:
                    ch = True
                    marks = [(mark.mark_value, mark.mark_criterion) for mark in subject.summative_list]
                    markA, markB, markC, markD = [0, 0], [0, 0], [0, 0], [0, 0]
                    for mark in sorted(marks, key=lambda x: x[1]):
                        if mark[1] == "A":
                            markA[0] += int(mark[0])
                            markA[1] += 1
                        elif mark[1] == "B":
                            markB[0] += int(mark[0])
                            markB[1] += 1
                        elif mark[1] == "C":
                            markC[0] += int(mark[0])
                            markC[1] += 1
                        elif mark[1] == "D":
                            markD[0] += int(mark[0])
                            markD[1] += 1
                        payload += f"**{mark[0]}**{mark[1]}"

                    if markA[1] == 0:
                        markA[1] = 1
                    if markB[1] == 0:
                        markB[1] = 1
                    if markC[1] == 0:
                        markC[1] = 1
                    if markD[1] == 0:
                        markD[1] = 1
                    payload += f" | __AVG:__ **{markA[0] / markA[1]}**A **{markB[0] / markB[1]}**B **{markC[0] / markC[1]}**C **{markD[0] / markD[1]}**D"
                if ch:
                    await self.client.send_message(
                        entity=await event.get_sender(),
                        message=payload,
                        parse_mode="md",
                        silent=True
                    )
        await event.answer("In beta")


class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    """
    Class for working with callback query
    """
