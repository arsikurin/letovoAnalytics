#  Made by arsikurin in 2022.

from app.bot.callbackquery.base import CBQueryBase

choose_an_option_below_text = "Choose an option below ↴"
back_btn_text = "« Back"


class CBQAccounts(CBQueryBase):
    pass

    # async def send_settings_page(self, sender: types.User) -> types.Message:
    #     """
    #     Send settings page
    #
    #     Args:
    #         sender (types.User): end user
    #
    #     Returns:
    #         types.Message
    #     """
    #     main_email = ""
    #     spare_emails = [
    #         "", ""
    #     ]
    #     buttons = [
    #         [
    #             types.InlineKeyboardButton(main_email, b"set_1"),
    #             types.InlineKeyboardButton("Active", b"set_1"),
    #             types.InlineKeyboardButton("Remove", b"remove_1")
    #         ]
    #     ]
    #     for i, email in enumerate(spare_emails):
    #         buttons.append(
    #             [
    #                 types.InlineKeyboardButton(email, f"set_{i + 2}"),
    #                 types.InlineKeyboardButton("Remove", f"remove_{i + 2}"),
    #             ]
    #         )
    #     if len(spare_emails) < 2:
    #         buttons.append(
    #             [
    #                 Button.url("Add", settings().URL_LOGIN_LOCAL),
    #             ]
    #         )
    #
    #     return await self.client.send_message(
    #         chat_id=sender.id,
    #         text="Settings",
    #         reply_markup=types.ReplyKeyboardMarkup(buttons
    #     )
    #
    # @staticmethod
    # async def set_account(event: types.CallbackQuery):
    #     sender: types.User = event.from_user
    #     to_active = int(event.data.split(b"_")[-1])
    #
    #     buttons = event.message.reply_markup
    #     choices = {1, 2, 3}
    #     choices.remove(to_active)
    #
    #     if len(buttons.rows[to_active - 1].buttons) == 3:
    #         await event.answer("Already in use!")
    #     else:
    #         choice = choices.pop()
    #         if len(buttons.rows[choice - 1].buttons) == 3:
    #             cur_active = choice - 1
    #         else:
    #             cur_active = choices.pop() - 1
    #         buttons.rows[cur_active].buttons.pop(1)
    #         buttons.rows[to_active - 1].buttons.insert(1, types.InlineKeyboardButton("Active", event.data))
    #         # TODO swap current active and future active accounts
    #         await event.edit_message_text(
    #             "settings",
    #             reply_markup=types.ReplyKeyboardMarkup(buttons)
    #         )
    #
    # @staticmethod
    # async def remove_account(event: types.CallbackQuery):
    #     sender: types.User = event.from_user
    #     to_remove = int(event.data.split(b"_")[-1])
    #     buttons: types.ReplyInlineMarkup = (await event.get_message()).reply_markup
    #
    #     if len(buttons.rows[to_remove - 1].buttons) == 3:
    #         await event.answer("Cannot remove address that is in use!")
    #     else:
    #         buttons.rows[to_remove - 1].buttons.clear()
    #         buttons.rows[to_remove - 1].buttons.append(Button.url("Add", settings().URL_LOGIN_LOCAL))
    #         # TODO remove account
    #         await event.edit_message_text(
    #             "settings",
    #             reply_markup=types.ReplyKeyboardMarkup(buttons)
    #         )
