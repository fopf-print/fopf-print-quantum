from __future__ import annotations

import typing

T = typing.TypeVar('T', bound=object)


class InstanceOrMock(typing.Generic[T]):
    '''
    Да, это просто dict_element, который можно инициализировать.

    mypy не позволит запихать сюда значение не того типа, но, когда
    запускаются тесты, сюда будет пихаться заглушка. И, т.к. мы не 'натравляем'
    mypy на тетсы, всё будет ок из-за duck typing)
    '''
    def __init__(self) -> None:
        self._instance: T | None = None

    def set(self, other: T) -> None:
        self._instance = other

    def get(self) -> T:
        if self._instance is None:
            raise RuntimeError('global value is not initialized')

        return self._instance


class _GlobalsMetaclass(type):
    def __new__(cls, clsname: str, superclasses: tuple, attributesdict: dict) -> _GlobalsMetaclass:
        return type.__new__(cls, clsname, superclasses, {'storage': dict[type, typing.Any]()})

    def __getitem__(cls, key: type[T]) -> InstanceOrMock[T]:
        # mypy матерится на аттрибут, который захардкожен в __init__
        if key not in cls.storage:                    # type: ignore[attr-defined]
            cls.storage[key] = InstanceOrMock[T]()    # type: ignore[attr-defined]

        return cls.storage[key]                       # type: ignore[attr-defined]


class Globals(metaclass=_GlobalsMetaclass):
    pass
