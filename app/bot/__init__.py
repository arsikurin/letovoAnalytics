from .callbackquery import CallbackQuery
from .inlinequery import InlineQuery

from telethon import TelegramClient
from config import settings

__all__ = ("CallbackQuery", "InlineQuery", "client")

client = TelegramClient("letovoAnalytics", settings().TG_API_ID, settings().TG_API_HASH)
