from enum import StrEnum

from aiogram import Bot, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from quantum.core.globals import GlobalValue
from quantum.entities.users import User
from quantum.keyboards import menu_keyboard
from quantum.services.users import create_user

# mypy: disable-error-code="union-attr"
# в aiogram много `smth | None`, которые зависят от usage-case-ов
# поэтому забьём на это)))


class ChangeableUserProperty(StrEnum):
    firstname = 'firstname'
    lastname = 'lastname'
    group = 'group'


class UserPropertyChangeCallback(CallbackData, prefix='registration_change_property'):
    what: ChangeableUserProperty


class RegisterUserCallback(CallbackData, prefix='do_registration'):
    ...


class RegistrationFlow(StatesGroup):
    registration_in_process = State()
    change_firstname = State()
    change_lastname = State()
    change_group = State()


router = Router()
bot = GlobalValue[Bot].get()


async def kb_builder(state: FSMContext):
    user_data = await state.get_data()

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=f'Имя: {user_data[ChangeableUserProperty.firstname]}',
            callback_data=UserPropertyChangeCallback(what=ChangeableUserProperty.firstname).pack(),
        ),
        InlineKeyboardButton(
            text=f'Фамилия: {user_data[ChangeableUserProperty.lastname]}',
            callback_data=UserPropertyChangeCallback(what=ChangeableUserProperty.lastname).pack(),
        ),
        InlineKeyboardButton(
            text=f'Группа: {user_data[ChangeableUserProperty.group]}',
            callback_data=UserPropertyChangeCallback(what=ChangeableUserProperty.group).pack(),
        ),
        InlineKeyboardButton(
            text='Зарегистрируй меня!',
            callback_data=RegisterUserCallback().pack(),
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def print_default_prompt(chat_id: int, state: FSMContext):
    massages_to_delete = (await state.get_data()).get('messages_to_delete', [])
    for chat_id, message_id in massages_to_delete:
        await bot.delete_message(chat_id, message_id)

    msg = await bot.send_message(
        chat_id=chat_id,
        text='Проверь свои данные. Они нужны, чтоб один из админов справился тебя опознать :)',
        reply_markup=(await kb_builder(state)).as_markup(),
    )
    await state.update_data({'messages_to_delete': [(chat_id, msg.message_id)]})


async def start(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationFlow.registration_in_process)
    await state.update_data(
        {
            ChangeableUserProperty.firstname: message.chat.first_name,
            ChangeableUserProperty.lastname: message.chat.last_name,
            ChangeableUserProperty.group: '<номер группы>',
        }
    )

    await print_default_prompt(message.chat.id, state)


@router.callback_query(UserPropertyChangeCallback.filter())
async def change_user_info_callback(
        callback: types.CallbackQuery,
        callback_data: UserPropertyChangeCallback,
        state: FSMContext,
):
    callback2state = {
        ChangeableUserProperty.firstname.value: RegistrationFlow.change_firstname,
        ChangeableUserProperty.lastname.value: RegistrationFlow.change_lastname,
        ChangeableUserProperty.group.value: RegistrationFlow.change_group,
    }

    await state.set_state(callback2state[callback_data.what])
    new_msg = await callback.message.reply('Окей, хорошо\nТогда скажи, как правильно')

    msgs: list = (await state.get_data()).get('messages_to_delete', [])
    await state.update_data({'messages_to_delete': msgs + [(callback.message.chat.id, new_msg.message_id)]})


@router.message(RegistrationFlow.change_firstname)
@router.message(RegistrationFlow.change_lastname)
@router.message(RegistrationFlow.change_group)
async def change_user_info_input_handler(message: types.Message, state: FSMContext):
    state2property = {
        RegistrationFlow.change_firstname: ChangeableUserProperty.firstname.value,
        RegistrationFlow.change_lastname: ChangeableUserProperty.lastname.value,
        RegistrationFlow.change_group: ChangeableUserProperty.group.value,
    }

    current_state = await state.get_state()
    msgs: list = (await state.get_data()).get('messages_to_delete', [])
    await state.update_data(
        {
            # там есть перегрузка __eq__ (и нормально .value не получить)
            state2property[current_state]: message.text,  # type: ignore[index]
            'messages_to_delete': msgs + [(message.chat.id, message.message_id)]
        }
    )
    await state.set_state(RegistrationFlow.registration_in_process)
    await print_default_prompt(message.chat.id, state)


@router.callback_query(RegisterUserCallback.filter())
async def do_registration_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    user_data = await state.get_data()
    await create_user(
        User(
            id=callback.message.chat.id,
            first_name=user_data[ChangeableUserProperty.firstname.value],
            last_name=user_data[ChangeableUserProperty.lastname.value],
            username=callback.message.chat.username,
        )
    )

    await callback.message.reply(
        'по идее готово',
        reply_markup=menu_keyboard,
    )
