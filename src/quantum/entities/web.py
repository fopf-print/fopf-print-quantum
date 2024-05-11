from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from quantum.entities import printing


class PingResponse(BaseModel):
    message: str = Field(description='ответ на /ping', default='pong')


class PrintingTaskWeb(BaseModel):
    id: UUID = Field(default='id-шник задачки на печать')
    parameters: printing.PrintingParameters | None = Field(description='параметры печати', default=None)

    @classmethod
    def from_internal(cls, task: printing.PrintingTask) -> Self:
        return cls(id=task.id, parameters=task.parameters)


class TryGetTaskResponse(BaseModel):
    task: PrintingTaskWeb | None = Field(description='возвращаем задачку, если нашли', default=None)
