# Тут куча ~~говна~~ кода, который нужен чтоб тестить бота
# Пока(?) есть возможность тестить только команды
#
# Если будет полезно - можно будет попробовать

import inspect
import typing
import pydantic

import aiogram

from quantum.core.bot_utils import mb_propagate_exceptions
from quantum.entities import users


class MockUser(users.User):
    # сюда добавлять properties
    # date: datetime  # (for example)

    # ну а так можно добавлять вычислимые properties
    @pydantic.computed_field
    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


class MockChat(pydantic.BaseModel):
    id: int | None = pydantic.Field(default=None)
    first_name: str | None = pydantic.Field(default=None)
    last_name: str | None = pydantic.Field(default=None)
    username: str | None = pydantic.Field(default=None)


class MockDocument(pydantic.BaseModel):
    file_id: str
    file_unique_id: str


class MockMessage(pydantic.BaseModel):
    from_user: MockUser | None
    chat: MockChat | None
    message_id: int = pydantic.Field(default=123)
    document: MockDocument | None = pydantic.Field(default=None)
    text: str | None = pydantic.Field(default=None)

    # вот эта хрень для внешнего использования
    answer_messages_contains: list[str] = pydantic.Field(default_factory=lambda: [])
    reply_messages_contains: list[str] = pydantic.Field(default_factory=lambda: [])

    # вот так симулируем ответ на сообщение
    async def answer(self, text: str, *args, **kwargs):
        self.answer_messages_contains.append(text)

    async def reply(self, text: str, *args, **kwargs):
        self.reply_messages_contains.append(text)

    def get_result(self) -> "('reply', 'answer')":
        return self.reply_messages_contains, self.answer_messages_contains


def icheck(_, instance):
    return type(instance) is MockMessage


setattr(aiogram.types.Message.__class__, '__instancecheck__', icheck)


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
            if 'state' in inspect.signature(func).parameters:
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs, state=None)
            else:
                wrapper = func
            _map[command] = wrapper
            return func
        return inner


class MockBot:
    def __init__(self, default_user: dict):
        self.default_user = MockUser(
            **default_user
        )
        self._map = MockDispatcher.cmd_2_handler_map

    async def command(self, cmd: str, **kwargs) -> (list[str], list[str]):
        defaults = {
            'from_user': self.default_user,
        }
        defaults.update(kwargs)
        defaults['chat'] = (defaults['from_user'] and MockChat(**defaults['from_user'].model_dump())) or MockChat()

        msg = MockMessage(text=cmd, **defaults)

        await mb_propagate_exceptions(self._map[cmd])(msg)

        return msg.get_result()

