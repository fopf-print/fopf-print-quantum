import asyncio
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from quantum.connectors import db_payments, db_users, http_yookassa
from quantum.core import db
from quantum.entities.payments import RefillPayment, YookassaId
from quantum.services import client_notification

logger = logging.getLogger(__name__)


async def create_refill_link(user_id: int, amount_cells: int) -> str:
    payment_obj = await http_yookassa.create_payment(amount_cells)

    await db_payments.write_refill_payment(
        RefillPayment(
            user_id=user_id,
            yookassa_id=payment_obj.id,
            amount_cents=amount_cells,
            description='Пополнение баланса через Юкассу',
        )
    )

    return payment_obj.confirmation.confirmation_url


async def update_refill_payments() -> None:
    logger.info('starting...')

    unconfirmed_payment: list[RefillPayment] = list(await db_payments.get_unconfirmed_payments())
    logger.info('looking for payments: %s', [p.yookassa_id for p in unconfirmed_payment])

    confirmed_payments_ids: set[YookassaId] = {
        YookassaId(UUID(payment_obj.id))  # fuck mupy! (не подсказал)
        for payment_obj in await http_yookassa.get_confirmed_payments(
            created_dttm_ge=datetime.now(tz=UTC) - timedelta(days=1),
        )
    }
    logger.info('confirmed payments: %s', confirmed_payments_ids)

    just_succeeded_payments = [
        payment for payment in unconfirmed_payment if payment.yookassa_id in confirmed_payments_ids
    ]

    if not just_succeeded_payments:
        logger.info('nothing found --> back to sleep')
        return

    logger.info('found JUST SUCCEEDED payments: %s', just_succeeded_payments)

    # вообще говоря, мб стоит свапнуть цикл и транзакцию
    # но т.к. это будет выполняться примерно раз в никогда, то пофиг))
    async with db.transaction():
        for payment in just_succeeded_payments:
            await db_users.refill_user_balance(
                user_id=payment.user_id,
                amount_cents_delta=payment.amount_cents,
            )

        await db_payments.confirm_payments(just_succeeded_payments)

    logger.info('balance refilled! --> notification')

    await asyncio.gather(
        *(
            client_notification.send_message(
                user_id=payment.user_id,
                message='Баланс пополнен на %.2f рублей' % (payment.amount_cents / 100),
            )
            for payment in just_succeeded_payments
        )
    )

    logger.info('notification done! --> back to sleep')
