from enum import Enum

from pydantic import BaseModel, Field


class PagesPerList(str, Enum):
    one_list_per_page = 'one_list_per_page'
    two_lists_per_page = 'two_lists_per_page'
    four_lists_per_page = 'four_lists_per_page'


class SingleBothSides(str, Enum):
    single_side_printing = 'single_side_printing'
    both_sides_printing = 'both_sides_printing'


class PrintingPolicy(BaseModel):
    lists_per_page: PagesPerList = Field(
        description='сколько страниц на листе',
        default='one_list_per_page'
    )
    n_sides_printing: SingleBothSides = Field(
        description='печатаем ли на обеих сторонах листа',
        default='single_side_printing',
    )


class PrintingTask(BaseModel):
    user_id: int = Field(description='id-шник пользователя')
    message_id: int = Field(description='id-шник сообщения, содержащего файл')
    printer_id: int = Field(description='id-шник принтера')
    policy: PrintingPolicy = Field(description='параметры печати')
