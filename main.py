#!/usr/bin/python3.9

# import re
# import logging as log
import requests as rq

from datetime import date
from telethon import Button, TelegramClient, events
from essential import LOGIN_URL_LOCAL, API_ID, API_HASH, BOT_TOKEN, update_data, is_inited, \
    send_certain_day_schedule, receive_token, receive_student_id, get_analytics_login

"https://s-api.letovo.ru/api/students/54405"
"https://s-api.letovo.ru/api/studentsimg/54405"

client = TelegramClient("letovoAnalytics", API_ID, API_HASH)

with rq.Session() as s:
    @client.on(events.NewMessage(pattern=r"(?i).*start"))
    async def handle_start(event):
        sender = await event.get_sender()
        chat_id: str = str(sender.id)
        await client.send_message(entity=sender,
                                  message=f'Greetings, **{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}**!',
                                  parse_mode="md",
                                  buttons=[
                                      Button.text("Start", resize=True, single_use=False)
                                  ])

        if not get_analytics_login(chat_id=chat_id):
            await client.send_message(entity=sender,
                                      message=f"I will help you access your schedule via Telegram.\n"
                                              "Initially, you should provide your login and password to"
                                              " [Letovo Analytics](s.letovo.ru).\n  "
                                              f'To do that click the button below\n'
                                              "__After logging into your account, click Start button again__",
                                      parse_mode="md",
                                      buttons=[
                                          Button.url(text="Log in",
                                                     url=f'{LOGIN_URL_LOCAL + "?chat_id=" + chat_id}')
                                      ])
            if not is_inited(chat_id=chat_id):
                update_data(chat_id=chat_id)
            raise events.StopPropagation

        await client.send_message(entity=sender,
                                  message="Choose an option below ↴",
                                  parse_mode="md",
                                  buttons=[[
                                      Button.inline("Personal data »", b"personal_data")
                                  ], [
                                      Button.inline("Entire schedule", b"entiredaySchedule")
                                  ], [
                                      Button.inline("Today's schedule", b"todaysSchedule"),
                                  ], [
                                      Button.inline("Certain day schedule »", b"certainDaySchedule"),
                                  ]])
        update_data(chat_id=chat_id, token=t if (t := receive_token(s, chat_id)) else "error")
        update_data(chat_id=chat_id, student_id=t if (t := receive_student_id(s, chat_id)) else "error")


    @client.on(events.CallbackQuery(data=b"personal_data"))
    async def handle_2(event):
        await event.edit("**Personal data page**\nHere will be the data that I store about you",
                         parse_mode="md",
                         buttons=[[
                             Button.inline("btn", b"")
                         ], [
                             Button.inline("« Back", b"back_main")
                         ]])


    @client.on(events.CallbackQuery(data=b"certainDaySchedule"))
    async def handle_certain(event):
        await event.edit("Choose a day below ↴",
                         parse_mode="md",
                         buttons=[[
                             Button.inline("Monday", b"monday")
                         ], [
                             Button.inline("Tuesday", b"tuesday")
                         ], [
                             Button.inline("Wednesday", b"wednesday")
                         ], [
                             Button.inline("Thursday", b"thursday")
                         ], [
                             Button.inline("Friday", b"friday")
                         ], [
                             Button.inline("Saturday", b"saturday")
                         ], [
                             Button.inline("« Back", b"back_main")
                         ]])


    @client.on(events.CallbackQuery(pattern=r"(?i).*day"))
    async def days(event):
        chat_id = str(event.original_update.user_id)

        if event.data == b"todaysSchedule":
            await send_certain_day_schedule(int(date.today().strftime("%w")) - 1, event, client, s, chat_id)

        elif event.data == b"entiredaySchedule":
            await send_certain_day_schedule(-10, event, client, s, chat_id)

        elif event.data == b"monday":
            await send_certain_day_schedule(0, event, client, s, chat_id)

        elif event.data == b"tuesday":
            await send_certain_day_schedule(1, event, client, s, chat_id)

        elif event.data == b"wednesday":
            await send_certain_day_schedule(2, event, client, s, chat_id)

        elif event.data == b"thursday":
            await send_certain_day_schedule(3, event, client, s, chat_id)

        elif event.data == b"friday":
            await send_certain_day_schedule(4, event, client, s, chat_id)

        elif event.data == b"saturday":
            await send_certain_day_schedule(5, event, client, s, chat_id)


    @client.on(events.CallbackQuery(data=b"back_main"))
    async def back_main(event):
        await event.edit("Choose an option below ↴",
                         parse_mode="md",
                         buttons=[[
                             Button.inline("Personal data »", b"personal_data")
                         ], [
                             Button.inline("Entire schedule", b"entiredaySchedule")
                         ], [
                             Button.inline("Today's schedule", b"todaysSchedule"),
                         ], [
                             Button.inline("Certain day schedule »", b"certainDaySchedule"),
                         ]])


    @client.on(events.NewMessage())
    async def handle_messages(event):
        if event.message.message != "Start":
            await event.delete()
        # await client.delete_messages(await event.get_sender(), event.message.id)


    if __name__ == "__main__":
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()

    # msg_id = event.original_update.msg_id
    # entity = event.query.peer
