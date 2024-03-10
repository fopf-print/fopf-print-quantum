from dataclasses import dataclass


@dataclass
class BusinessLogicFucked(Exception):
    msg: list[str]

    def __str__(self):
        return f'BusinessLogicFucked({self.msg=})'

    def __repr__(self):
        return self.__str__()
