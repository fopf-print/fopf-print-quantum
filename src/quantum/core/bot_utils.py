import functools
import typing

import aiogram
from aiogram import types

from quantum.connectors.db_users import is_user_exists
from quantum.core.exceptions import BusinessLogicFucked

# есть три ~~стула~~ термина:
# - идентификация
# - аутентификация
# - авторизация
#
# Для понимания разницы, расскажу сказку))
# Приходит Даня к Серверу и говорит
# - Привет, Сервер!) Я - Даня
# После этих слов Сервер знает, что Я откликаюсь на 'Даня'.
# Это _идентификация_)
#
# Тут сервис задумался, а правда ли тот, кто назвался 'Даня'
# на самом деле является Даней. И тут Сервер говорит
# - Слушай, Даня, а докажи, что ты - Даня. Скажи пароль)
# - Пароль 'fopf123' -- ответил Даня
# Прим. рассказчика: тут в реальности будет хэш пароля, но пофиг.
# - Ну вроде правда Даня. Окей, зачем пришёл?
# Теперь Сервер уверен, что Даня - это Даня. Это _аутентификация_
#
# - А покажи ка мне, Сервер, сообщения других пользователей!
# - Ща, сек - я проверю, хватает ли у тебя, Даня, прав на это дело...
# - блин...
# - А вот фиг тебе! Прав не хватает! This incident will be reported
# А это - _авторизация_
#
# Вот и сказочке конец, а кто слушал - пройдёт собес на джуна)
#
#
# Сами условия вложены друг в друга:
#   authorization < authentication < identification
# Где запись `A < B` значит, что выполнение `A` влечёт выполнение `B`
# (в целом это логично)
#
# Короче термины лучше понимать, чтоб знать, что делают эти декораторы
# И, если допустимо использовать несколько декораторов, лучше выбирать
# самый слабый из допустимых)

F = typing.TypeVar('F', bound=typing.Callable[..., typing.Any])


def user_identified(func: F) -> F:
    """
    Проверяем, что можем идентифицировать пользователя
    В случае ошибки пишем сообщение (и в будующем логируем ошибку)

    Применяем этот декоратор для команд, в которых необходимо знать, с
    каким именно пользователем мы взаимодействуем в данный момент
    """
    @functools.wraps(func)
    async def wrapper(smth: types.Message | types.CallbackQuery, *args, **kwargs) -> None:
        # а почему не тернарник?
        # https://github.com/python/mypy/issues/4134
        if isinstance(smth, types.Message):
            msg = smth
        else:
            msg = typing.cast(types.Message, smth.message)

        if msg.chat.id is None:
            raise BusinessLogicFucked(msg=['USER_IS_UNIDENTIFIED'])

        await func(smth, *args, **kwargs)
    return typing.cast(F, wrapper)


def user_registered(func: F) -> F:
    """
    Проверяем, что пользователь зарегистрирован
    (существует у нас в бд-шке)
    """
    cache: dict[int, bool] = {}  # тут memory leak, но похуй

    async def cached_is_user_exists(user_id: int) -> bool:
        if cache.get(user_id):
            return True
        if await is_user_exists(user_id):
            cache[user_id] = True
            return True
        return False

    @functools.wraps(func)
    @user_identified  # требуем выполнения более слабого условия
    async def wrapper(smth: types.Message | types.CallbackQuery, *args, **kwargs) -> None:
        # а почему не тернарник?
        # https://github.com/python/mypy/issues/4134
        if isinstance(smth, types.Message):
            msg = smth
        else:
            msg = typing.cast(types.Message, smth.message)

        if await cached_is_user_exists(msg.chat.id):  # type: ignore[union-attr]
            await func(smth, *args, **kwargs)
            return

        raise BusinessLogicFucked(msg=['USER_IS_NOT_EXISTS'])

    return typing.cast(F, wrapper)


def mb_propagate_exceptions(func: F) -> F:
    """
    Потом тут надо будет добавить немного вариативности

    TODO:
    При запуске в тестовом окружении ловит исключения и отправляет их пользаку.
    При запуске в prod-окружении ловит исключения, логирует их и отправляет пользаку
    сообщение чуть красивше 'что-то пошло не так'
    """
    @functools.wraps(func)
    async def wrapper(smth: types.Message | types.CallbackQuery, *args, **kwargs) -> None:
        # а почему не тернарник?
        # https://github.com/python/mypy/issues/4134
        if isinstance(smth, types.Message):
            msg = smth
        else:
            msg = typing.cast(types.Message, smth.message)

        try:
            await func(smth, *args, **kwargs)
        except BusinessLogicFucked as blf:
            await msg.answer(f'Got some errors: {blf.msg}')

    return typing.cast(F, wrapper)


class DecoratedDispatcher(aiogram.Dispatcher):
    """
    Есть надобность декорировать почти все обработчики
    Ну и т.к. немного лень (да и некрасиво) делать это явно, существует
    этот костыль.
    """
    def __getattr__(self, name) -> typing.Any:
        if name not in ('message', 'callback_query'):
            return getattr(super(), name)

        return mb_propagate_exceptions(getattr(super(), name))
