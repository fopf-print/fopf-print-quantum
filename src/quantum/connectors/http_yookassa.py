from datetime import UTC, datetime
from uuid import uuid4

from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse

from quantum import settings

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_API_KEY


async def create_payment(value_cents: int, description: str | None = None) -> PaymentResponse:
    description = description or ('Пополнение на %.2f рублей' % (value_cents / 100))
    return Payment.create(
        params={
            'amount': {
                'value': '%.2f' % (value_cents / 100),
                'currency': 'RUB',
            },
            # TODO: сделать нормально (тут редирект не нужен)
            'confirmation': {
                'type': 'redirect',
                'return_url': settings.REDIRECT_AFTER_PAYMENT_URL,
            },
            'capture': True,
            'description': description,
        },
        idempotency_key=uuid4(),
    )


async def get_confirmed_payments(created_dttm_ge: datetime) -> list[PaymentResponse]:
    dt: str = created_dttm_ge.astimezone(UTC).isoformat()
    return Payment.list(
        params={
            'created_at.gt': dt,
            'status': 'succeeded',
        },
    ).items
