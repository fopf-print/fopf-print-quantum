from uuid import UUID, uuid4

from quantum.core import db


async def write_refill_payment(
        user_id: int,
        yookassa_id: UUID,
        amount_cents: int,
        description: str,
) -> UUID:
    id_ = uuid4()
    await db.fetchall(
        """
        insert into payments_log (id, yookassa_id, user_id, amount_cents, description, is_confirmed)
        values ($1, $2, $3, $4, $5, false)
        returning id
        """,
        (id_, yookassa_id, user_id, amount_cents, description)
    )
    return id_
