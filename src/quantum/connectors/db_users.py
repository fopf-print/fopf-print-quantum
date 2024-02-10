from quantum.core import db
from quantum.entities import users


async def create_new_user(user_info: users.User) -> None:
    await db.execute(
        'insert into users values (?, ?, ?, ?, ?)',
        [
            user_info.id,
            user_info.first_name,
            user_info.last_name,
            user_info.username,
            user_info.balance_cents,
        ]
    )


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
