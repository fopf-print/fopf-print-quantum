from quantum.core import db
from quantum.core.exceptions import BusinessLogicFucked
from quantum.entities import users


async def is_user_exists(user_id: int) -> bool:
    return bool(next(
        iter(await db.fetchall('select 1 from users where id = $1', [user_id])),
        False,
    ))


async def get_user_info(user_id: int) -> users.User | None:
    info = next(
        iter(await db.fetchall('select * from users where id = $1', [user_id])),
        None
    )

    if not info:
        return None

    return users.User(
        **info
    )


async def upsert_user_info(user_info: users.User) -> None:
    is_exists = next(
        iter(await db.fetchall('select id from users where id = $1', [user_info.id])),
        False
    )

    if not is_exists:
        await db.execute(
            'insert into users values ($1, $2, $3, $4, $5)',
            [
                user_info.id,
                user_info.first_name,
                user_info.last_name,
                user_info.username,
                0,
            ]
        )
        return

    await db.execute(
        '''
        update users
        set
            first_name = $1
            last_name = $2
            username = $3
        where id = $4''',
        [
            user_info.first_name,
            user_info.last_name,
            user_info.username,
            user_info.id,
        ]
    )


async def _change_user_balance(user_id: int, balance_cents_increment: int) -> int:
    """
    Списываем у пользователя user_id balance_cents_delta.
    Если balance_cents_delta < 0 то баланс будет пополнен

    :returns: новый баланс пользователя
    """
    new_balance = await db.fetchall(
        """
        update users
        set balance_cents = balance_cents + $2
        where id = $1
        returning balance_cents
        """,
        (user_id, balance_cents_increment),
    )

    if not new_balance or new_balance[0].get('balance_cents') is None:
        raise BusinessLogicFucked(msg=['USER_IS_NOT_EXISTS'])

    return int(new_balance[0]['balance_cents'])


async def write_off_user_balance(user_id: int, amount_cents_delta: int) -> int:
    """
    Списываем у пользователя user_id balance_cents_delta.

    :returns: новый баланс пользователя
    """
    assert amount_cents_delta > 0
    return await _change_user_balance(user_id, -amount_cents_delta)


async def refill_user_balance(user_id: int, amount_cents_delta: int) -> int:
    """
    Добавляем пользователю user_id balance_cents_delta на баланс

    :returns: новый баланс пользователя
    """
    assert amount_cents_delta > 0
    return await _change_user_balance(user_id, amount_cents_delta)
