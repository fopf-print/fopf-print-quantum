import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode

from quantum import settings
from quantum.bot import fopf_print_bot


def fopf_print_bot_worker() -> None:
    while True:
        bot = Bot(settings.FOPF_PRINT_BOT_TOKEN, parse_mode=ParseMode.HTML)
        asyncio.run(fopf_print_bot.start_polling(bot))
