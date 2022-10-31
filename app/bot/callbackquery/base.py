#  Made by arsikurin in 2022.

import abc
import asyncio
import datetime
import logging as log
import typing

import aiohttp
from pyrogram import Client, types

from app.dependencies import API, Postgresql, Firestore, errors as errors_l, types as types_l
from app.schemas import ScheduleAndHWResponse


class CBQueryBase(abc.ABC):
    """
    Class for dealing with callback query messages

    Args:
        session (aiohttp.ClientSession): an instance of `TelegramClient` with credentials filled in
        session (aiohttp.ClientSession): an instance of `aiohttp.ClientSession`
        db (Postgresql): connection to the database with users' usage analytics
        fs (Firestore): connection to the database with users' credentials
    """
    __slots__ = ("client", "_api", "_db", "_fs", "__payload", "__msg_ids")

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
                if hasattr(err, "__notes__"):
                    notes = f". \n{err.__notes__}"
                else:
                    notes = ""
                await event.answer(f"[✘] {err}{notes}", show_alert=True)
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
                log.critical("Specific day value not provided!")
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
                if hasattr(err, "__notes__"):
                    notes = f". \n{err.__notes__}"
                else:
                    notes = ""
                await event.answer(f"[✘] {err}{notes}", show_alert=True)
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
