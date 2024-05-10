from typing import NewType
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

RefillPaymentId = NewType('RefillPaymentId', UUID)
"""Суррогатный айдишник пополнения"""

YookassaId = NewType('YookassaId', UUID)
"""Внутренний айдишник yokass-ы"""


class RefillPayment(BaseModel):
    user_id: int = Field(description='идентификатор пользователя')
    yookassa_id: YookassaId = Field(description='идентификатор платежа юкассы')
    amount_cents: int = Field(description='сумма пополнения')
    description: str = Field(description='описание платежа')
    id: RefillPaymentId = Field(description='идентификатор платежа', default_factory=uuid4)
