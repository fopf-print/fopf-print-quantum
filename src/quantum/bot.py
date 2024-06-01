from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from quantum import keyboards
from quantum.bot_user_flow import refill_balance_flow, registration_flow, set_printing_parameters_flow
from quantum.connectors import db_users
from quantum.core.bot_utils import user_identified, user_registered
from quantum.core.globals import GlobalValue
from quantum.services.balance import get_user_balance
from quantum.services.printing import process_file

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это)))

bot = GlobalValue[Bot].get()
fopf_print_bot = GlobalValue[Dispatcher].get()

fopf_print_bot.include_routers(refill_balance_flow.router)
fopf_print_bot.include_routers(registration_flow.router)
fopf_print_bot.include_routers(set_printing_parameters_flow.router)


# Тут идут обработчики команд
# Обработчики нажатий кнопок будут дальше внизу

@fopf_print_bot.message(CommandStart())
@fopf_print_bot.message(Command("menu"))
async def show_menu_handler(message: types.Message):
    if await db_users.is_user_exists(message.chat.id):
        menu_markup = keyboards.menu_keyboard
    else:
        menu_markup = keyboards.unregistered_user_menu_keyboard

    await message.answer(
        "Зачем ты разбудил меня, смертный?",
        reply_markup=menu_markup,
    )


@fopf_print_bot.message(Command('whoami'))
async def command_whoami_handler(message: types.Message):
    await message.reply(
        f'user_id: {message.chat.id=}' + '\n'
        f'first_name: {message.chat.first_name=}' + '\n'
        f'last_name: {message.chat.last_name=}' + '\n'
        f'username: {message.chat.username=}' + '\n'
    )


@fopf_print_bot.message(Command('register'))
@user_identified
async def command_register(message: types.Message, state: FSMContext):
    if await db_users.is_user_exists(message.chat.id):
        await message.reply('ты уже смешарик')
        return

    await registration_flow.start(message, state)


@fopf_print_bot.message(Command('print'))
@user_registered
async def print_handler(message: types.Message):
    await message.answer("Просто отправь файлик")


@fopf_print_bot.message(Command('balance'))
@user_identified
async def show_balance_handler(message: types.Message):
    balance: float = (await get_user_balance(message.chat.id)) or 0.0
    await message.answer(f'Ваш баланс: {balance} рубликов')


@fopf_print_bot.message(Command('refill'))
@user_registered
async def balance_refill_handler(message: types.Message, state: FSMContext):
    await refill_balance_flow.start(message, state)


@fopf_print_bot.message(F.document)
@user_registered
async def document_for_print_handler(message: types.Message, state: FSMContext):
    """
    Тут начинается флоу печати
    """
    if not message.document.file_name.endswith('.pdf'):
        await message.answer('пока умею печатать только pdf-ки :(')
        return

    printing_task_id = await process_file(message.chat.id, message.document.file_id, message.message_id)

    await set_printing_parameters_flow.start(printing_task_id=printing_task_id, message=message, state=state)


# Ниже обработка нажатий клавиатуры

@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.print_thing.value)
@user_registered
async def btn_print(message: types.Message):
    await message.answer("Просто отправь файлик")


@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.check_balance.value)
@user_registered
async def btn_check_balance(message: types.Message):
    await show_balance_handler(message)


@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.add_balance.value)
@user_registered
async def btn_add_balance(message: types.Message, state: FSMContext):
    await refill_balance_flow.start(message, state)
