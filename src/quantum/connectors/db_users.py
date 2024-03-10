from quantum.core import db
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
