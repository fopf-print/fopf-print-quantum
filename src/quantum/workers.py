import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from quantum import settings
from quantum.core.bot_utils import DecoratedDispatcher
from quantum.core.globals import GlobalValue


def fopf_print_bot_worker() -> None:
    GlobalValue[Bot].set(Bot(settings.FOPF_PRINT_BOT_TOKEN, parse_mode=ParseMode.HTML))
    GlobalValue[Dispatcher].set(DecoratedDispatcher())

    from quantum.bot import fopf_print_bot

    bot = GlobalValue[Bot].get()
    while True:
        asyncio.run(fopf_print_bot.start_polling(bot))
