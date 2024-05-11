from enum import StrEnum

from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


class MenuButtonsText(StrEnum):
    print_thing = '🖨 Как напечатать штуку'
    check_balance = '🐖 Проверить баланс'
    add_balance = '💰 Пополнить баланс'


menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=MenuButtonsText.print_thing)],
        [KeyboardButton(text=MenuButtonsText.check_balance), KeyboardButton(text=MenuButtonsText.add_balance)],
    ],
    resize_keyboard=False,
)


unregistered_user_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='/register')]],
    resize_keyboard=False,
)
