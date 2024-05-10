from quantum.core import db
from quantum.entities.payments import RefillPayment, RefillPaymentId


async def write_refill_payment(
        rpayment: RefillPayment,
) -> RefillPaymentId:
    await db.fetchall(
        """
        insert into payments (id, yookassa_id, user_id, amount_cents, description, is_confirmed)
        values ($1, $2, $3, $4, $5, false)
        returning id
        """,
        (rpayment.id, rpayment.yookassa_id, rpayment.user_id, rpayment.amount_cents, rpayment.description),
    )
    return rpayment.id


async def get_unconfirmed_payments() -> list[RefillPayment]:
    payments = await db.fetchall(
        """
        select
             id
            ,yookassa_id
            ,user_id
            ,amount_cents
            ,description
        from
            payments
        where
            1=1
            and not is_confirmed
            and transaction_dttm > now() at time zone 'utc' - interval '24 hours'
        """,
    )
    return [RefillPayment.model_validate(p) for p in payments]


async def confirm_payments(payments: list[RefillPayment]) -> None:
    await db.execute(
        """
        update payments
        set is_confirmed = true
        where id = any($1)
        """,
        [
            (p.id,)
            for p in payments
        ],
    )
