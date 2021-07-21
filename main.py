# !/usr/bin/python3.9

import firebase_admin
# import sqlite3
# import re

from telethon import Button, TelegramClient, events
from essential import init_user, LOGIN_URL_LOCAL, API_ID, API_HASH, BOT_TOKEN
from firebase_admin import credentials

"https://s-api.letovo.ru/api/students/54405"
"https://s-api.letovo.ru/api/studentsimg/54405"

client = TelegramClient("letovoAnalytics", API_ID, API_HASH)
cred_obj = credentials.Certificate("fbAdminConfig.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    "databaseURL": "https://authtest-3fcb2-default-rtdb.europe-west1.firebasedatabase.app/"
})


@client.on(events.NewMessage(pattern=r"(?i).*start"))
async def handle_start(event):
    sender = await event.get_sender()
    print(sender, "\n\n")
    print(sender.lang_code)
    await client.send_message(entity=sender,
                              message=f"""Hello, **{sender.first_name} {sender.last_name}**!\n  I will help you """
                                      """getting access to your schedule via Telegram.\nAt first, you should provide """
                                      """your login and password to [Letovo Analytics](s.letovo.ru).\n  To do that """
                                      f"""click [this]({LOGIN_URL_LOCAL + "?chat_id=" + str(sender.id)}) link""",
                              parse_mode="md",
                              buttons=[
                                  Button.text("Start", resize=True, single_use=False),
                              ])
    init_user(chat_id=str(sender.id))
    # await client.send_message(entity=sender,
    #                           message="Choose an option below ↴",
    #                           parse_mode="md",
    #                           buttons=[[
    #                               Button.inline("Personal data ->", b"personal_data")
    #                           ], [
    #                               Button.inline("2nd btn", b""),
    #                           ]])


@client.on(events.CallbackQuery(data=b"personal_data"))
async def handle_quiz(event):
    await event.edit("**Personal data page**",
                     parse_mode="md",
                     file="sandbox.py",
                     buttons=[[
                         Button.inline("1st btn", b"")
                     ], [
                         Button.inline("<- Back", b"back_main")
                     ]])


@client.on(events.CallbackQuery(data=b"back_main"))
async def handle_quiz(event):
    await event.edit("**Choose an option below ↴**",
                     parse_mode="md",
                     buttons=[[
                         Button.inline("Personal data ->", b"personal_data")
                     ], [
                         Button.inline("2nd btn", b""),
                     ]])


if __name__ == "__main__":
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()

# event.delete()
# client.delete_messages(sender, msg_id)
# msg_id = event.original_update.msg_id
# entity = event.query.peer
