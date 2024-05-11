from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    message: str = Field(description='ответ на /ping', default='pong')
