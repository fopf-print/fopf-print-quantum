from quantum.core import db
from quantum.entities import users


async def is_user_exists(user_id: int) -> bool:
    return bool(next(
        iter(await db.fetchall('select 1 from users where id = ?', [user_id])),
        False,
    ))


async def get_user_info(user_id: int) -> users.User | None:
    info = next(
        iter(await db.fetchall('select * from users where id = ?', [user_id])),
        None
    )

    if not info:
        return None

    return users.User(
        **info
    )


async def upsert_user_info(user_info: users.User) -> None:
    is_exists = next(
        iter(await db.fetchall('select id from users where id = ?', [user_info.id])),
        False
    )

    if not is_exists:
        await db.execute(
            'insert into users values (?, ?, ?, ?, ?)',
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
            first_name = ?
            last_name = ?
            username = ?
        where id = ?''',
        [
            user_info.first_name,
            user_info.last_name,
            user_info.username,
            user_info.id,
        ]
    )


async def update_user_balance(user_id: int, balance_cents_delta: int) -> bool:
    async with db.transaction() as tr:
        current_balance = next(
            iter(await tr.execute('select balance from users where id = ?', [user_id])),
            {'balance': None},
        )['balance']

        if not current_balance:  # пользователь не существует
            return False

        if current_balance + balance_cents_delta < 0:  # недостаточно средств
            return False

        await tr.execute(
            'update users set balance_cents = balance_cents + ? where id = ?',
            [balance_cents_delta, user_id]
        )

    return True
