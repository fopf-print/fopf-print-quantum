from enum import StrEnum

from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder


class MenuButtonsText(StrEnum):
    print_thing = '🖨 Распечатать штуку'
    check_balance = '🐖 Проверить баланс'
    add_balance = '💰 Пополнить баланс'


menu_keyboard = ReplyKeyboardBuilder()
menu_keyboard.add(
    KeyboardButton(text=MenuButtonsText.print_thing),
    KeyboardButton(text=MenuButtonsText.check_balance),
    KeyboardButton(text=MenuButtonsText.add_balance),
)
menu_keyboard.adjust(1)


unregistered_user_menu_keyboard = ReplyKeyboardBuilder()
unregistered_user_menu_keyboard.add(
    KeyboardButton(text='/register')
)
