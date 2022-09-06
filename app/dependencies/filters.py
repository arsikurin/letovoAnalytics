import pyrogram
from pyrogram import types


async def web_app_filter(_, __, m: types.Message):
    return bool(m.web_app_data)


web_app = pyrogram.filters.create(web_app_filter)
