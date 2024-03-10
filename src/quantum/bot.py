from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold

from quantum.connectors import db_users
from quantum.core.bot_utils import user_identified, user_registered
from quantum.core.globals import GlobalValue
from quantum.entities.users import User
from quantum.services.balance import get_user_balance
from quantum.services.printing import create_printing_task
from quantum.services.users import create_user

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это)))

bot = GlobalValue[Bot].get()
fopf_print_bot = GlobalValue[Dispatcher].get()


# Тут идут обработчики команд
# Обработчики нажатий кнопок будут дальше внизу

@fopf_print_bot.message(CommandStart())
async def command_start_handler(message: types.Message):
    """
    TODO: придумать и написать красивое welcome-сообщение
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@fopf_print_bot.message(Command('register'))
@user_identified
async def command_register(message: types.Message):
    await create_user(
        User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
    )
    await message.reply('Done!)')


@fopf_print_bot.message(Command('balance'))
@user_identified
async def command_balance(message: types.Message):
    balance: float = (await get_user_balance(message.from_user.id)) or 0.0
    await message.answer(f'Ваш баланс: {balance} рубликов')


@fopf_print_bot.message(F.document)
@user_registered
async def document_for_print_handler(message: types.Message):
    if not message.document.file_name.endswith('.pdf'):
        await message.answer('пока умею печатать только pdf-ки :(')
        return

    await create_printing_task(
        user_id=message.from_user.id,
        message_id=message.message_id,
        file_id=message.document.file_id,
    )


# Теперь вот отсюда вниз идёт описание клавиатуры
# В будущем может разнесём это на 2 отдельных файлика
# Но пока вроде нормально и так)

class BalanceAction(CallbackData, prefix="balance"):
    action: str
    amount: int


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
@user_registered
async def btn_check_balance(message: types.Message):
    await command_balance(message)


@fopf_print_bot.message(F.text.lower() == 'пополнить баланс')
@user_registered
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
@user_registered
async def send_random_value(callback: types.CallbackQuery, callback_data: BalanceAction, *args, **kwargs):
    amount = callback_data.amount

    user_id = callback.from_user.id
    user_info = await db_users.get_user_info(user_id)

    if user_info is None:
        await db_users.upsert_user_info(
            User(
                id=user_id,
                first_name=callback.from_user.first_name,
                last_name=callback.from_user.last_name,
                username=callback.from_user.username,
                balance_cents=0
            )
        )

    await db_users.update_user_balance(user_id, amount*100)
    user_info = await db_users.get_user_info(user_id)
    await callback.message.answer(
        f'Пополнение прошло успешно! Ваш новый баланс: {user_info.balance_cents / 100}'
    )
    await callback.answer()


@fopf_print_bot.message(F.text.lower() == 'распечатать штуку')
@user_registered
async def btn_print(message: types.Message):
    await command_balance(message)
