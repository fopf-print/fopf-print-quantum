from uuid import UUID

from aiogram import Bot, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from quantum.connectors import db_printing
from quantum.core.globals import GlobalValue
from quantum.entities.printing import PrintingParameters
from quantum.services import printing

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это))


class PrintingParametersChangeCallback(CallbackData, prefix='printing_parameters_change'):
    what: str


class DoPrintingCallback(CallbackData, prefix='do_printing'):
    ...


class PrintingParametersChangeFlow(StatesGroup):
    select_parameter_to_change = State()


router = Router()
bot = GlobalValue[Bot].get()


async def kb_builedr(state: FSMContext):
    data = await state.get_data()  # noqa F841

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text='Печетать страницы: все',
            callback_data=PrintingParametersChangeCallback(what='nothing').pack(),
        ),
        InlineKeyboardButton(
            text='Страниц на листе: одна',
            callback_data=PrintingParametersChangeCallback(what='nothing').pack(),
        ),
        InlineKeyboardButton(
            text='Двусторонняя печать: нет',
            callback_data=PrintingParametersChangeCallback(what='nothing').pack(),
        ),
        InlineKeyboardButton(
            text='Цветная печать: нет',
            callback_data=PrintingParametersChangeCallback(what='nothing').pack(),
        ),
        InlineKeyboardButton(
            text='Принтер: ещё бы про лакировку спросил',
            callback_data=PrintingParametersChangeCallback(what='nothing').pack(),
        ),
        InlineKeyboardButton(
            text='На печать!',
            callback_data=DoPrintingCallback().pack(),
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def print_printing_parameters(state: FSMContext):
    data = await state.get_data()
    chat_id: int | str = data['chat_id']
    message_id: int = data['message_id']
    task_id: UUID = data['printing_task_id']

    printing_cost_cents = await printing.calculate_cost(task_id)
    printing_cost_fmt = '{:.2f}'.format(printing_cost_cents / 100)

    await bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=message_id,
        text=(
            'Настрой параметры и отправь на печать\n'
            f'стоимость: {printing_cost_fmt}'
        ),
        reply_markup=(await kb_builedr(state)).as_markup(),
    )


async def start(printing_task_id: UUID, message: types.Message, state: FSMContext):
    # await state.clear()
    await state.set_state(PrintingParametersChangeFlow.select_parameter_to_change)
    await state.update_data(
        {
            'printing_task_id': printing_task_id,
            'chat_id': message.chat.id,
            'message_id': message.message_id,
            'пофиг': 'пока да',
        }
    )

    await print_printing_parameters(state)


@router.callback_query(PrintingParametersChangeCallback.filter())
async def change_printing_parameters_callback(
        callback: types.CallbackQuery,
        callback_data: PrintingParametersChangeCallback,
        state: FSMContext,
):
    await callback.message.reply('unimplemented :(')
    await print_printing_parameters(state)


@router.callback_query(DoPrintingCallback.filter())
async def do_printing_callback(
        callback: types.CallbackQuery,
        callback_data: DoPrintingCallback,
        state: FSMContext,
):
    data = await state.get_data()
    printing_task_id = data['printing_task_id']
    await state.clear()

    await db_printing.set_parameters(
        printing_task_id,
        PrintingParameters(),
    )

    await printing.schedule_printing(printing_task_id)
