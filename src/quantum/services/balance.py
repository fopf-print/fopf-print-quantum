from quantum.connectors import db_users
from quantum.core import db
from quantum.core.exceptions import BusinessLogicFucked


async def get_user_balance(user_id: int) -> float | None:
    user_info = await db_users.get_user_info(user_id)

    if user_info is None:
        return None

    return user_info.balance_cents / 100


async def update_user_balance(user_id: int, balance_cents_delta: int) -> int:
    async with db.transaction():
        user_info = await db_users.get_user_info(user_id)

        if not user_info:
            raise BusinessLogicFucked(msg=['USER_IS_NOT_EXISTS'])

        if user_info.balance_cents + balance_cents_delta < 0:
            raise BusinessLogicFucked(msg=['NOT_ENOUGH_MONEY'])

        user_info.balance_cents += balance_cents_delta
        await db_users.upsert_user_info(user_info)
    return user_info.balance_cents
