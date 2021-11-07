#!/usr/bin/python3.10

import asyncio
import requests as rq

from telethon import Button, events
from app.dependencies import Weekdays, MarkTypes, NothingFoundError, UnauthorizedError, Firebase, Web
from app.schemas import MarksResponse, ScheduleResponse
from config import settings


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
    __slots__ = ("client", "session")

    def __init__(self, c, s):
        self.client = c
        self.session = s

    async def send_greeting(self, sender):
        payload = f'{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}'.strip()
        await self.client.send_message(
            entity=sender,
            message=f'Greetings, **{payload}**!',
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
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
                Button.url(text="Click here to log in", url=f'{settings().URL_LOGIN_LOCAL}?chat_id={sender.id}')
            ]
        )

    async def send_stats(self, sender, db):
        for user in await db.get_users():
            _ = ("sender_id", "message_id", "schedule_counter", "homework_counter", "marks_counter",
                 "holidays_counter", "clear_counter", "options_counter", "help_counter", "about_counter",
                 "inline_counter")
            resp = await db.get_analytics(user[0])
            if not any((resp[2], resp[3], resp[4], resp[5], resp[7], resp[8])):
                continue
            name = await Firebase.get_name(resp[0])
            surname = await Firebase.get_surname(resp[0])
            name = name if name is not NothingFoundError else ""
            surname = surname if surname is not NothingFoundError else ""
            await self.client.send_message(
                entity=sender,
                message=f"ID: {resp[0]}\nName: {name} {surname}\nSchedule: {resp[2]}\nHomework {resp[3]}\n"
                        f"Marks: {resp[4]}\nHolidays: {resp[5]}\nOptions: {resp[7]}\n"
                        f"Help: {resp[8]}\nAbout: {resp[9]}",
                parse_mode="md"
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
            message="I can help you access s.letovo.ru resources via Telegram. "
                    "If you're new here, please see the [Terms of Use](https://example.com).\n"
                    "\n"
                    "**You can control me by sending these commands:**\n"
                    "\n"
                    "**/start** - restart bot. You'll get a welcome message\n"
                    "**/about** - get info about the bot developers\n"
                    "**/options** - get a menu of options that the bot can serve\n"
                    "**/help** - get this manual page\n"
                    "**/schedule** - get schedule from s.letovo.ru\n"
                    "**/marks** - get marks from s.letovo.ru\n"
                    "**/homework** - get homework from s.letovo.ru **[beta]**\n"
                    "\n"
                    "\n"
                    "**Bot Settings**\n"
                    "__coming soon__\n"
                    "\n"
                    "**Marks UI**\n"
                    "**0..8**A — Summative A\n"
                    "**0..8**B — Summative B\n"
                    "**0..8**C — Summative C\n"
                    "**0..8**D — Summative D\n"
                    "**0..8**F — Formative\n",
            parse_mode="md",
            link_preview=False
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

    async def send_dev_page(self, sender):
        await self.client.send_message(
            entity=sender,
            message="Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Statistics", b"stats")
                ], [
                    Button.inline("Update tokens", b"tokens"),
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
            self, event: events.CallbackQuery.Event, specific_day: Weekdays
    ):
        """
        parse and send specific day(s) from schedule

        :param event: a return object of CallbackQuery
        :param specific_day: day number or -10 to send entire schedule
        """
        schedule_future = await Web.receive_hw_n_schedule(self.session, str(event.sender_id))
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
                message=f"__{specific_day.name}, {int(date[2]) + specific_day.value - 1}.{date[1]}.{date[0]}__\n",
                parse_mode="md",
                silent=True
            )

        for day in schedule_response.data:
            if day.schedules and specific_day.value in (int(day.period_num_day), -10):
                wd = Weekdays(int(day.period_num_day)).name
                if specific_day.value == -10 and wd != old_wd:
                    await self.client.send_message(
                        entity=await event.get_sender(),
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
                    entity=await event.get_sender(),
                    message=payload,
                    parse_mode="md",
                    silent=True,
                    link_preview=False
                )
                old_wd = wd
        await event.answer()

    async def send_homework(
            self, event: events.CallbackQuery.Event, specific_day: Weekdays
    ):
        """
        parse and send specific day(s) from homework

        :param event: a return object of CallbackQuery
        :param specific_day: day number or -10 to send all homework
        """
        homework_future = await Web.receive_hw_n_schedule(self.session, str(event.sender_id))
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
            self, event: events.CallbackQuery.Event, specific: MarkTypes
    ):
        """
        parse and send marks

        :param event: a return object of CallbackQuery
        :param specific: all, sum, recent
        """
        marks_future = await Web.receive_marks(self.session, str(event.sender_id))
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
                if abs(mark_a_avg % 1) < settings().EPS:
                    mark_a_avg = round(mark_a_avg)
                else:
                    mark_a_avg = round(mark_a_avg, 1)
                if abs(mark_b_avg % 1) < settings().EPS:
                    mark_b_avg = round(mark_b_avg)
                else:
                    mark_b_avg = round(mark_b_avg, 1)
                if abs(mark_c_avg % 1) < settings().EPS:
                    mark_c_avg = round(mark_c_avg)
                else:
                    mark_c_avg = round(mark_c_avg, 1)
                if abs(mark_d_avg % 1) < settings().EPS:
                    mark_d_avg = round(mark_d_avg)
                else:
                    mark_d_avg = round(mark_d_avg, 1)
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
                    if abs(mark_a_avg % 1) < settings().EPS:
                        mark_a_avg = round(mark_a_avg)
                    else:
                        mark_a_avg = round(mark_a_avg, 1)
                    if abs(mark_b_avg % 1) < settings().EPS:
                        mark_b_avg = round(mark_b_avg)
                    else:
                        mark_b_avg = round(mark_b_avg, 1)
                    if abs(mark_c_avg % 1) < settings().EPS:
                        mark_c_avg = round(mark_c_avg)
                    else:
                        mark_c_avg = round(mark_c_avg, 1)
                    if abs(mark_d_avg % 1) < settings().EPS:
                        mark_d_avg = round(mark_d_avg)
                    else:
                        mark_d_avg = round(mark_d_avg, 1)
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
