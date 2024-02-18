from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from quantum.connectors import db_users
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from quantum.entities.users import User
from aiogram.filters.callback_data import CallbackData


fopf_print_bot = Dispatcher()


class BalanceAction(CallbackData, prefix="balance"):
    action: str
    amount: int


@fopf_print_bot.message(CommandStart())
async def command_start_handler(message: types.Message):
    """Отвечаем на /start"""
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")  # type: ignore


@fopf_print_bot.message(Command('balance'))
async def command_balance(message: types.Message):
    user_id = message.from_user.id
    user_info = await db_users.get_user_info(user_id)
    print(user_id)
    balance = 0
    if user_info is not None:
        balance = user_info.balance_cents/100
    await message.answer(f'Ваш баланс: {balance} рубликов')  # type: ignore


@fopf_print_bot.message(Command("menu"))
async def show_menu(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Распечатать штуку'))
    builder.add(types.KeyboardButton(text='Проверить баланс'))
    builder.add(types.KeyboardButton(text='Пополнить баланс'))
    await message.answer(
        "Зачем ты разбудил меня, смертный?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@fopf_print_bot.message(F.text.lower() == 'проверить баланс')
async def btn_check_balance(message: types.Message):
    await command_balance(message)


@fopf_print_bot.message(F.text.lower() == 'пополнить баланс')
async def btn_deposit(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="50",
        callback_data=BalanceAction(
            action='add',
            amount=50
        )
    )
    builder.button(
        text="100",
        callback_data=BalanceAction(
            action='add',
            amount=100
        )
    )

    await message.answer(
        "Выберите сумму пополнения или введите свою:",
        reply_markup=builder.as_markup()
    )


@fopf_print_bot.callback_query(BalanceAction.filter(F.action == 'add'))
async def send_random_value(callback: types.CallbackQuery, callback_data: BalanceAction, *args, **kwargs):
    print(callback)
    amount = callback_data.amount

    user_id = callback.from_user.id
    print(user_id)
    user_info = await db_users.get_user_info(user_id)

    if user_info is None:
        await db_users.upsert_user_info(
            User(
                id=user_id,
                first_name=callback.message.from_user.first_name,
                last_name=callback.message.from_user.last_name,
                username=callback.message.from_user.username,
                balance_cents=0
            )
        )

    await db_users.update_user_balance(user_id, amount*100)
    user_info = await db_users.get_user_info(user_id)
    print(user_info.balance_cents)
    await callback.message.answer(f'Пополнение прошло успешно! Ваш новый баланс: {user_info.balance_cents / 100}')
    await callback.answer()


@fopf_print_bot.message(F.text.lower() == 'распечатать штуку')
async def btn_print(message: types.Message):
    await command_balance(message)
