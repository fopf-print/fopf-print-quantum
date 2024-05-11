import json
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PrintingTaskStatus(StrEnum):
    cost_calculating = 'cost_calculating'
    parameters_input = 'parameters_input'
    printing = 'printing'
    done = 'done'
    failed = 'failed'
    deleted = 'deleted'


class PagesLimit(BaseModel):
    page_from: int = Field(description='с какой страницы печатать')
    page_to: int = Field(description='по какую страницу печатать')


class PagesPerList(StrEnum):
    one_page_per_list = 'one_page_per_list'
    two_pages_per_list = 'two_pages_per_list'
    four_pages_per_list = 'four_pages_per_list'


class PrintingParameters(BaseModel):
    page_limits: PagesLimit | None = Field(description='обрезка страниц', default=None)
    pages_per_list: PagesPerList = Field(description='сколько страниц на листе', default=PagesPerList.one_page_per_list)
    double_sided_flg: bool = Field(description='двусторонняя печать', default=False)
    color_printing_flg: bool = Field(description='цветная печать', default=False)


class PrintingTask(BaseModel):
    id: UUID = Field(default='id-шник задачки на печать')
    file_id: str = Field(description='id-шник файла')
    user_id: int = Field(description='id-шник пользователя')
    message_id: int = Field(description='id-шник сообщения, содержащего файл')
    cost_cents: int = Field(description='стоимость печати')
    status: PrintingTaskStatus | None = Field(description='статус таски')
    parameters: PrintingParameters | None = Field(description='параметры печати', default=None)
    created_dttm: datetime | None = Field(description='время создания таски', default=None)
    updated_dttm: datetime | None = Field(description='последнее время обновления статуса', default=None)

    @field_validator('parameters', mode='before')
    @classmethod
    def parameters_validator(cls, parameters: Any):
        if not isinstance(parameters, str):
            return parameters

        return PrintingParameters.model_validate(json.loads(parameters))
