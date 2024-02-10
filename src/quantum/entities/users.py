from pydantic import BaseModel, Field


class User(BaseModel):
    id: int = Field(description='тг-айдишник пользователя')
    first_name: str | None = Field(description='имя')
    last_name: str | None = Field(description='фамилия')
    username: str | None = Field(description='username')
    balance_cents: int = Field(description='копеек осталось на счёте', default=0)
