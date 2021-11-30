#!/usr/bin/python3.10
import typing

import requests as rq
from telethon import types, events

from app.dependencies import NothingFoundError, UnauthorizedError, Weekdays, Web


class InlineQueryEventEditors:
    """
    Class for working with inline query events
    """

    @staticmethod
    async def to_main_page(event: events.InlineQuery.Event):
        """
        display main page in inline query
        """

        await event.answer(
            results=[
                event.builder.article(
                    title="Holidays",
                    description="send message with vacations terms",
                    text="__after__ **unit I**\n31.10.2021 — 07.11.2021\n\n"
                         "__after__ **unit II**\n26.12.2021 — 09.01.2022\n\n"
                         "__after__ **unit III**\n13.03.2022 — 20.03.2022\n\n"
                         "__after__ **unit IV**\n22.05.2022 — 31.08.2022",
                    thumb=types.InputWebDocument(
                        url="https://letovo-analytics.web.app/static/images/icons/calendar-icon.png",
                        size=512,
                        mime_type="image/jpg",
                        attributes=[
                            types.DocumentAttributeImageSize(
                                w=512,
                                h=512
                            )
                        ]
                    )
                ),
                event.builder.photo(file="static/images/icons/schedule.jpg")
            ], switch_pm="Log in", switch_pm_param="inlineMode"
        )


class InlineQuerySenders:
    __slots__ = ("session",)

    def __init__(self, s):
        self.session = s

    async def send_schedule(  # TODO
            self, event: events.InlineQuery.Event, specific_day: int
    ):
        """
        parse and send specific day(s) from schedule to inline query

        :param event: a return object of InlineQuery
        :param specific_day: day number or -10 to send entire schedule
        """

        schedule_future = await Web.receive_hw_n_schedule(self.session, str(event.sender_id))
        if schedule_future == UnauthorizedError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Cannot get data from s.letovo.ru",
                        text="[✘] Cannot get data from s.letovo.ru"
                    )
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        if schedule_future == NothingFoundError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Nothing found in database for this user.\nPlease, enter /start and register",
                        text="[✘] Nothing found in database for this user.\nPlease, enter /start and register"
                    )
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        if schedule_future == rq.ConnectionError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Cannot establish connection to s.letovo.ru",
                        text="[✘] Cannot establish connection to s.letovo.ru"
                    )
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        # if specific_day == 0:
        #     return await event.answer(
        #         results=[
        #             event.builder.article(title=f"{day_name} lessons", text="Congrats! It's Sunday, no lessons")
        #         ], switch_pm="Log in", switch_pm_param="inlineMode"
        #     )
        payload = ""
        old_wd = 0
        schedule = schedule_future.result().json()["data"]
        date = schedule[0]["date"].split("-")
        payload += f'<em>{Weekdays(specific_day).name}, {int(date[2]) + specific_day - 1}.{date[1]}.{date[0]}</em>\n'

        for day in schedule:
            if len(day["schedules"]) > 0 and specific_day in (int(day["period_num_day"]), -10):
                wd = Weekdays(int(day["period_num_day"])).name
                if specific_day == -10 and wd != old_wd:
                    payload += f'\n<strong>=={wd}==</strong>\n'

                payload += f'{day["period_name"]} | <em>{day["schedules"][0]["room"]["room_name"]}</em>:\n'
                payload += f'<strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} {day["schedules"][0]["group"]["group_name"]}</strong>\n'
                if day["schedules"][0]["zoom_meetings"]:
                    payload += f'[ZOOM]({day["schedules"][0]["zoom_meetings"][0]["meeting_url"]}\n)'
                payload += f'{day["period_start"]} — {day["period_end"]}\n'
                payload += "\n"
                old_wd = wd

        await event.answer(
            results=[
                event.builder.article(title=f'{Weekdays(specific_day).name} lessons', text=payload, parse_mode="html")
            ], switch_pm="Log in", switch_pm_param="inlineMode"
        )


@typing.final
class InlineQuery(InlineQueryEventEditors, InlineQuerySenders):
    """
    Class for working with inline query
    """
