from quantum.connectors import db_balance, db_users


async def get_user_balance(user_id: int) -> float | None:
    user_info = await db_users.get_user_info(user_id)

    if user_info is None:
        return None

    return user_info.balance_cents / 100


async def update_user_balance(user_id: int, balance_cents_delta: int) -> int:
    return await db_balance.update_user_balance(user_id, balance_cents_delta)
