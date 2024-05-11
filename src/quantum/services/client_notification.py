from aiogram import Bot

from quantum.core.globals import GlobalValue


async def send_message(user_id: int, message: str):
    bot = GlobalValue[Bot].get()
    await bot.send_message(chat_id=user_id, text=message)


async def send_printing_complete(user_id: int, message_id: int):
    bot = GlobalValue[Bot].get()
    await bot.send_message(
        chat_id=user_id,
        reply_to_message_id=message_id,
        text='Печать закончена, можно забирать'
    )


async def send_printing_failed(user_id: int, message_id: int):
    bot = GlobalValue[Bot].get()
    await bot.send_message(
        chat_id=user_id,
        reply_to_message_id=message_id,
        text='Что-то пошло не так, пни техподдержку пожалуйста: @DanilaManakov'
    )
