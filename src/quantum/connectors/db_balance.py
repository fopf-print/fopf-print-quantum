from quantum.core import db
from quantum.core.exceptions import BusinessLogicFucked


async def update_user_balance(user_id: int, balance_cents_delta: int) -> int:
    async with db.transaction():
        current_balance: int | None = next(
            iter(await db.fetchall('select balance_cents from users where id = $1', [user_id])),
            {'balance_cents': None},
        )['balance_cents']

        if current_balance is None:
            raise BusinessLogicFucked(msg=['USER_IS_NOT_EXISTS'])

        if current_balance + balance_cents_delta < 0:
            raise BusinessLogicFucked(msg=['NOT_ENOUGH_MONEY'])

        new_balance = current_balance + balance_cents_delta

        await db.execute(
            'update users set balance_cents = $1 where id = $2',
            [new_balance, user_id]
        )

    return new_balance
