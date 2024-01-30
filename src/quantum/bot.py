from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

fopf_print_bot = Dispatcher()


@fopf_print_bot.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """Отвечаем на /start"""
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")  # type: ignore
