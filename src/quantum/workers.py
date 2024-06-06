import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from quantum import settings
from quantum.core.bot_utils import DecoratedDispatcher
from quantum.core.globals import GlobalValue

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def fopf_print_bot_worker() -> None:
    GlobalValue[Bot].set(Bot(settings.fopf_print_bot_token, parse_mode=ParseMode.HTML))
    GlobalValue[Dispatcher].set(DecoratedDispatcher())

    from quantum.bot import fopf_print_bot

    bot = GlobalValue[Bot].get()
    while True:
        asyncio.run(fopf_print_bot.start_polling(bot))


def refill_worker() -> None:
    """
    Этот воркер проходится по id-шникам юкассы и проверяет, была ли по ним совершена оплата
    """
    logger.setLevel(logging.INFO)
    GlobalValue[Bot].set(Bot(settings.fopf_print_bot_token, parse_mode=ParseMode.HTML))

    from quantum.services.payments import update_refill_payments

    async def aworker() -> None:
        while True:
            await update_refill_payments()
            await asyncio.sleep(settings.refill_worker_delay_sec)

    asyncio.run(aworker())
