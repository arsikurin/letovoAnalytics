import typing

from telethon.tl.types import UserStatusRecently


class UserProfilePhoto(typing.Protocol):
    photo_id: int
    dc_id: int
    has_video: bool
    stripped_thumb: None


class User(typing.Protocol):
    id: int
    is_self: bool
    contact: bool
    mutual_contact: bool
    deleted: bool
    bot: bool
    bot_chat_history: bool
    bot_nochats: bool
    verified: bool
    restricted: bool
    min: bool
    bot_inline_geo: bool
    support: bool
    scam: bool
    apply_min_photo: bool
    fake: bool
    access_hash: int
    first_name: str | None
    last_name: str | None
    username: str | None
    phone: None
    photo: UserProfilePhoto
    status = UserStatusRecently()
    bot_info_version: None
    restriction_reason: list
    bot_inline_placeholder: None
    lang_code: str
