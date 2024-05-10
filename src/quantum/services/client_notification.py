from aiogram import Bot

from quantum.core.globals import GlobalValue


async def send_message(user_id: int, message: str):
    bot = GlobalValue[Bot].get()
    await bot.send_message(chat_id=user_id, text=message)
