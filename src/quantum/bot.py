from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from quantum import keyboards
from quantum.bot_user_flow import registration_flow
from quantum.connectors.db_users import is_user_exists
from quantum.core.bot_utils import user_identified, user_registered
from quantum.core.globals import GlobalValue
from quantum.services.balance import get_user_balance, update_user_balance
from quantum.services.printing import create_printing_task

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это)))

bot = GlobalValue[Bot].get()
fopf_print_bot = GlobalValue[Dispatcher].get()

fopf_print_bot.include_routers(registration_flow.router)


class BalanceAddFlow(StatesGroup):
    input_amount = State()


# Тут идут обработчики команд
# Обработчики нажатий кнопок будут дальше внизу

@fopf_print_bot.message(CommandStart())
@fopf_print_bot.message(Command("menu"))
async def show_menu_handler(message: types.Message):
    if await is_user_exists(message.chat.id):
        menu_markup = keyboards.menu_keyboard.as_markup(resize_keyboard=True)
    else:
        menu_markup = keyboards.unregistered_user_menu_keyboard.as_markup(resize_keyboard=True)

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
    if await is_user_exists(message.chat.id):
        await message.reply('ты уже смешарик')
        return

    await registration_flow.start(message, state)


@fopf_print_bot.message(Command('balance'))
@user_identified
async def show_balance_handler(message: types.Message):
    balance: float = (await get_user_balance(message.chat.id)) or 0.0
    await message.answer(f'Ваш баланс: {balance} рубликов')


@fopf_print_bot.message(F.document)
@user_registered
async def document_for_print_handler(message: types.Message):
    if not message.document.file_name.endswith('.pdf'):
        await message.answer('пока умею печатать только pdf-ки :(')
        return

    await create_printing_task(
        user_id=message.chat.id,
        message_id=message.message_id,
        file_id=message.document.file_id,
    )


# Теперь вот отсюда вниз идёт описание клавиатуры
# В будущем может разнесём это на 2 отдельных файлика
# Но пока вроде нормально и так)


@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.print_thing.value)
@user_registered
async def btn_print(message: types.Message):
    await show_balance_handler(message)


@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.check_balance.value)
@user_registered
async def btn_check_balance(message: types.Message):
    await show_balance_handler(message)


@fopf_print_bot.message(F.text == keyboards.MenuButtonsText.add_balance.value)
@user_registered
async def btn_deposit(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите сумму пополнения или введите свою чиселкой:",
        reply_markup=keyboards.deposit_inline_keyboard.as_markup()
    )
    await state.set_state(BalanceAddFlow.input_amount)


@fopf_print_bot.message(BalanceAddFlow.input_amount, ~F.text.isdigit())
@user_registered
async def recieve_any_amount_add_balance_handler(message: types.Message, state: FSMContext):
    await message.reply(
        'В следующий раз подставь числа в буквы и упрости выражение\n'
        'Очень хотелось увидеть на входе число)'
    )
    await state.clear()


@fopf_print_bot.message(BalanceAddFlow.input_amount, F.text.isdigit())
@user_registered
async def receive_any_amount_add_balance_handler(message: types.Message, state: FSMContext):
    # не None, ибо .isdigit()
    amount_delta = int(message.text) * 100  # type: ignore[arg-type]

    user_id = message.chat.id
    await state.clear()

    new_balance_cents = await update_user_balance(user_id, amount_delta)
    await message.answer(f'Пополнение прошло успешно! Ваш новый баланс: {new_balance_cents / 100}')


@fopf_print_bot.callback_query(keyboards.DepositActionData.filter())
@user_registered
async def send_random_value(
        callback: types.CallbackQuery,
        callback_data: keyboards.DepositActionData,
        state: FSMContext,
):
    amount_delta = callback_data.amount
    user_id = callback.message.chat.id
    await state.clear()

    new_balance_cents = await update_user_balance(user_id, amount_delta)
    await callback.message.answer(f'Пополнение прошло успешно! Ваш новый баланс: {new_balance_cents / 100}')
    await callback.answer()
