import typing

import requests as rq
from pyrogram import types

from app.dependencies import errors as errors_l, types as types_l, API


class InlineQueryEventEditors:
    """
    Class for working with inline query events
    """

    @staticmethod
    async def to_main_page(event: types.InlineQuery):
        """
        display main page in inline query
        """
        await event.answer(
            results=[
                types.InlineQueryResultArticle(
                    title="Holidays",
                    description="send message with vacations terms",
                    input_message_content=types.InputTextMessageContent(
                        "__after__ **unit I**\n31.10.2021 — 07.11.2021\n\n"
                        "__after__ **unit II**\n26.12.2021 — 09.01.2022\n\n"
                        "__after__ **unit III**\n13.03.2022 — 20.03.2022\n\n"
                        "__after__ **unit IV**\n22.05.2022 — 31.08.2022"),
                    thumb_url="https://letovo-analytics.web.app/static/images/icons/calendar-icon.png",
                ),
                types.InlineQueryResultPhoto(
                    title="schedule",
                    photo_url="https://letovo-analytics.web.app/static/images/icons/letovo-transp.png"
                ),
            ], switch_pm_text="Register", switch_pm_parameter="inlineMode", is_gallery=False, cache_time=0
        )


class InlineQuerySenders:
    # TODO implement search of lessons
    __slots__ = ("session",)

    def __init__(self, s):
        self.session = s

    async def send_schedule(
            self, event: types.InlineQuery, specific_day: int
    ):
        """
        parse and send specific day(s) from schedule to inline query

        :param fs: firestore connection object
        :param event: a return object of InlineQuery
        :param specific_day: day number or -10 to send entire schedule
        """
        schedule_future = await API.receive_schedule_and_hw(sender_id=str(event.from_user.id))
        if schedule_future == errors_l.UnauthorizedError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Cannot get data from s.letovo.ru",
                        text="[✘] Cannot get data from s.letovo.ru"
                    )
                ], switch_pm="Register", switch_pm_param="inlineMode"
            )

        if schedule_future == errors_l.NothingFoundError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Nothing found in database for this user.\nPlease, enter /start and register",
                        text="[✘] Nothing found in database for this user.\nPlease, enter /start and register"
                    )
                ], switch_pm="Register", switch_pm_param="inlineMode"
            )

        if schedule_future == rq.ConnectionError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title="[✘] Cannot establish connection to s.letovo.ru",
                        text="[✘] Cannot establish connection to s.letovo.ru"
                    )
                ], switch_pm="Register", switch_pm_param="inlineMode"
            )

        # if specific_day == 0:
        #     return await event.answer(
        #         results=[
        #             event.builder.article(title=f"{day_name} lessons", text="Congrats! It's Sunday, no lessons")
        #         ], switch_pm="Register", switch_pm_param="inlineMode"
        #     )
        payload = ""
        old_wd = 0
        schedule = schedule_future.result().json()["data"]
        date = schedule[0]["date"].split("-")
        payload += f'<em>{types_l.Weekdays(specific_day).name}, {int(date[2]) + specific_day - 1}.{date[1]}.{date[0]}</em>\n'

        for day in schedule:
            if len(day["schedules"]) > 0 and specific_day in (int(day["period_num_day"]), -10):
                wd = types_l.Weekdays(int(day["period_num_day"])).name
                if specific_day == -10 and wd != old_wd:
                    payload += f'\n<strong>=={wd}==</strong>\n'

                payload += f'{day["period_name"]} | <em>{day["schedules"][0]["room"]["room_name"]}</em>:\n'
                payload += f'<strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} ' \
                           f'{day["schedules"][0]["group"]["group_name"]}</strong>\n'
                if day["schedules"][0]["zoom_meetings"]:
                    payload += f'[ZOOM]({day["schedules"][0]["zoom_meetings"][0]["meeting_url"]}\n)'
                payload += f'{day["period_start"]} — {day["period_end"]}\n'
                payload += "\n"
                old_wd = wd

        await event.answer(
            results=[
                event.builder.article(title=f'{types_l.Weekdays(specific_day).name} lessons', text=payload,
                                      parse_mode="html")
            ], switch_pm="Register", switch_pm_param="inlineMode"
        )


@typing.final
class InlineQuery(InlineQueryEventEditors, InlineQuerySenders):
    """
    Class for working with inline query
    """
