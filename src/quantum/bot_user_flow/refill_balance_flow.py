from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

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


async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(RefillFlow.refill_by_link)

    await message.answer(
        "Выберите сумму пополнения или введите свою чиселкой:",
        reply_markup=deposit_inline_keyboard.as_markup()
    )


@router.callback_query(RefillCallbackData.filter())
async def refill_value_input_by_kb(
        callback: types.CallbackQuery,
        callback_data: RefillCallbackData,
        state: FSMContext,
):
    value_cents: int = callback_data.amount * 100
    await callback.message.reply(f'Ввод: {value_cents / 100}')
    await state.clear()


@router.message(RefillFlow.refill_by_link)
@router.message(RefillFlow.refill_by_embedded)
@router.message(RefillFlow.refill_without_payment)
async def refill_value_input_by_text(message: types.Message, state: FSMContext):
    try:
        value_cents = int(message.text) * 100  # type: ignore[arg-type]
    except ValueError:
        await message.reply(f"'{message.text}' is not a valid number :(")
        return

    await message.reply(f'Ввод: {value_cents / 100}')
    await state.clear()
