from quantum.connectors import db_payments, http_yookassa


async def create_refill_link(user_id: int, amount_cells: int) -> str:
    payment_obj = await http_yookassa.create_payment(amount_cells)

    await db_payments.write_refill_payment(
        user_id=user_id,
        yookassa_id=payment_obj.id,
        amount_cents=amount_cells,
        description='Пополнение баланса',
    )

    return payment_obj.confirmation.confirmation_url
