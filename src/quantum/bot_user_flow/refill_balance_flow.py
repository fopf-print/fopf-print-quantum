from aiogram import Bot, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from quantum.core.globals import GlobalValue
from quantum.services import payments

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это)))


class RefillFlow(StatesGroup):
    refill_by_link = State()
    refill_by_embedded = State()
    refill_without_payment = State()  # for debug


class RefillCallbackData(CallbackData, prefix='add_balance'):
    amount: int


deposit_inline_keyboard = InlineKeyboardBuilder()
deposit_inline_keyboard.add(
    *(
        InlineKeyboardButton(text=str(amount), callback_data=RefillCallbackData(amount=amount).pack())
        for amount in (10, 50, 100)
    )
)


router = Router()
bot = GlobalValue[Bot].get()


async def start(message: types.Message, state: FSMContext, no_payment: bool = False):
    await state.clear()
    await state.set_state(RefillFlow.refill_without_payment if no_payment else RefillFlow.refill_by_link)

    await message.answer(
        "Выберите сумму пополнения или введите свою чиселкой:",
        reply_markup=deposit_inline_keyboard.as_markup()
    )


async def _send_payment_instructions(user_id: int, amount_cents: int):
    url = await payments.create_refill_link(user_id=user_id, amount_cells=amount_cents)

    # TODO: сделать нормально
    await bot.send_message(
        chat_id=user_id,
        text=(
            'Ссылочка на оплату: ' + url + '\n'
            'После совершения оплаты деньги зачислятся через +-минуту (если нет - помогите Даше найти жулика...)'
        ),
    )


@router.callback_query(RefillCallbackData.filter())
async def refill_value_input_by_kb(
        callback: types.CallbackQuery,
        callback_data: RefillCallbackData,
        state: FSMContext,
):
    user_id: int = callback.from_user.id
    amount_cents: int = callback_data.amount * 100

    await state.clear()
    await _send_payment_instructions(user_id=user_id, amount_cents=amount_cents)


@router.message(RefillFlow.refill_by_link)
@router.message(RefillFlow.refill_by_embedded)
@router.message(RefillFlow.refill_without_payment)
async def refill_value_input_by_text(message: types.Message, state: FSMContext):
    user_id: int = message.from_user.id
    try:
        amount_cents = int(message.text) * 100  # type: ignore[arg-type]
    except ValueError:
        await message.reply(f"'{message.text}' is not a valid number :(")
        return

    await state.clear()
    await _send_payment_instructions(user_id=user_id, amount_cents=amount_cents)
