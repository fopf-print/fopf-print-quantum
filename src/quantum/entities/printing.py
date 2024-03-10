from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class PrintingTaskStatus(str, Enum):
    new = 'new'
    ready_to_pay = 'ready_to_pay'
    ready_to_convert = 'ready_to_convert'
    ready_to_print = 'ready_to_print'
    printed = 'printed'
    failed = 'failed'


class PagesPerList(str, Enum):
    one_page_per_list = 'one_page_per_list'
    two_pages_per_list = 'two_pages_per_list'
    four_pages_per_list = 'four_pages_per_list'


class NSidedPrinting(str, Enum):
    single_sided = 'single_sided'
    double_sided = 'double_sided'


class ColorPrinting(str, Enum):
    black_and_white = 'black_and_white'
    more_colors = 'more_colors'


class PrintingPolicy(BaseModel):
    page_from: int = Field(
        description='с какой страницы печатать',
        default=0,
    )
    page_to: int | None = Field(
        description='по какую страницу печатать',
        default=None,
    )
    lists_per_page: PagesPerList = Field(
        description='сколько страниц на листе',
        default=PagesPerList.one_page_per_list,
    )
    n_sides_printing: NSidedPrinting = Field(
        description='печатаем ли на обеих сторонах листа',
        default=NSidedPrinting.single_sided,
    )
    used_colors: ColorPrinting = Field(
        description='цветная печать или черно-белая',
        default=ColorPrinting.black_and_white,
    )


class PrintingTask(BaseModel):
    id: UUID = Field(default='id-шник задачки на печать')
    user_id: int = Field(description='id-шник пользователя')
    message_id: int = Field(description='id-шник сообщения, содержащего файл')
    file_id: str = Field(description='id-шник файла')
    status: PrintingTaskStatus = Field(description='статус таски')
    policy: PrintingPolicy | None = Field(description='параметры печати')
