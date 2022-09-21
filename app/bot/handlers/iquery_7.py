import pyrogram
from pyrogram import Client, types

from app.bot import InlineQuery
from app.dependencies import types as types_l, Firestore


async def init(clients: types_l.Clients[Client], iQuery: InlineQuery, fs: Firestore):
    client = clients.client_i

    @client.on_inline_query()
    async def _inline_query(_client: Client, inline_query: types.InlineQuery):
        sender: types.User = inline_query.from_user
        sender_id = str(sender.id)

        if not await fs.is_logged(sender_id=sender_id):
            await inline_query.answer(switch_pm_text="Log in", switch_pm_parameter="inlineMode")
            raise pyrogram.StopPropagation
        await iQuery.to_main_page(event=inline_query)

        # send_schedule = ft.partial(
        #     iQuery.send_schedule,
        #     event=event
        # )
        # match types_l.MatchWeekdays(inline_query.query):
        #     case types_l.MatchWeekdays(next=True):
        #         # TODO next day inline query
        #         await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
        #         # await event.answer([
        #         #     builder.article(title="Next lesson", text=text if text else "No schedule found in analytics")
        #         # ], switch_pm="Log in", switch_pm_param="inlineMode")
        #     case types_l.MatchWeekdays(today=True):
        #         await send_schedule(specific_day=int(datetime.datetime.now().strftime("%w")))
        #     case types_l.MatchWeekdays(monday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Monday.value)
        #     case types_l.MatchWeekdays(tuesday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Tuesday.value)
        #     case types_l.MatchWeekdays(wednesday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Wednesday.value)
        #     case types_l.MatchWeekdays(thursday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Thursday.value)
        #     case types_l.MatchWeekdays(friday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Friday.value)
        #     case types_l.MatchWeekdays(saturday=True):
        #         await send_schedule(specific_day=types_l.Weekdays.Saturday.value)
        #     case types_l.MatchWeekdays(entire=True):
        #         await send_schedule(specific_day=types_l.Weekdays.ALL.value)
        #     case _:
        #         await iQuery.to_main_page(event=inline_query)
