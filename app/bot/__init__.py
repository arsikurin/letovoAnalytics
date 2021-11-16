from telethon import TelegramClient

from config import settings
from .callbackquery import CallbackQuery
from .inlinequery import InlineQuery

__all__ = ("CallbackQuery", "InlineQuery", "client")

client = TelegramClient("letovoAnalytics", api_id=settings().TG_API_ID, api_hash=settings().TG_API_HASH)
