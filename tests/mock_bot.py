# Тут куча ~~говна~~ кода, который нужен чтоб тестить бота
# Пока(?) есть возможность тестить только команды
#
# Если будет полезно - можно будет попробовать

import typing
import pydantic
import pytest

import aiogram

from quantum.entities import users


class MockUser(users.User):
    # сюда добавлять properties
    # date: datetime  # (for example)

    # ну а так можно добавлять вычислимые properties
    @pydantic.computed_field
    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


class MockMessage:
    def __init__(
            self,
            from_user: MockUser,
            text: str | None = None,
            message_id: int = 123,
    ):
        # сюда можно добавлять другие properties
        # если обработчик требует больше
        self.from_user = from_user
        self.message_id = message_id
        self.text = text

        # это не property, сюда сохраняются все ответы
        self._reply: list[str] = []

    # вот так симулируем ответ на сообщение
    async def answer(self, text: str, *args, **kwargs):
        self._reply.append(text)

    def get_reply(self):
        return self._reply


class IgnoreShit(type):
    def __getattr__(cls, name):
        def do_nothing_decorator(*args, **kwargs):
            print(f'{name}(*{args}, **{kwargs}) will be ignored')

            if args and isinstance(args[0], typing.Callable):
                return args[0]

            return lambda x: x
        return do_nothing_decorator


class MockDispatcher(metaclass=IgnoreShit):
    cmd_2_handler_map = {}

    @classmethod
    def message(cls, *filters):
        if len(filters) != 1:
            print(f'handler will be ignored: {filters}')
            return lambda x: x

        fltr = filters[0]
        if not isinstance(fltr, aiogram.filters.Command):
            print(
                'handler will be ignored; \n'
                f'expected @message(fltr: aiogram.filters.Command), got {filters}'
            )
            return lambda x: x

        command = f'/{fltr.commands[0]}'
        _map = cls.cmd_2_handler_map

        def inner(func: typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]:
            _map[command] = func
            return func  # да, у нас тут без других побочных действий
        return inner


class MockBot:
    def __init__(self, default_user):
        self.default_user = MockUser(
            **default_user.model_dump()
        )
        self._map = MockDispatcher.cmd_2_handler_map

    async def command(self, cmd: str, **kwargs) -> list[str]:
        if 'from_user' not in kwargs:
            kwargs['from_user'] = self.default_user

        msg = MockMessage(text=cmd, **kwargs)

        await self._map[cmd](msg)

        return msg.get_reply()

