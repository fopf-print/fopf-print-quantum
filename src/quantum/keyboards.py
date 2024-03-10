from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardButton, ReplyKeyboardBuilder


class MenuButtonsText(str, Enum):
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


class DepositActionData(CallbackData, prefix='add_balance'):
    amount: int


deposit_inline_keyboard = InlineKeyboardBuilder()
deposit_inline_keyboard.add(
    *(
        InlineKeyboardButton(text=str(amount), callback_data=DepositActionData(amount=amount).pack())
        for amount in (10, 50, 100)
    )
)
