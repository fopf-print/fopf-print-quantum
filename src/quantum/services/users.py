from quantum.connectors import db_users
from quantum.core.exceptions import BusinessLogicFucked
from quantum.entities import users


async def create_user(user_info: users.User) -> None:
    if await db_users.is_user_exists(user_info.id):
        raise BusinessLogicFucked(msg=['USER_ALREADY_EXISTS'])

    await db_users.upsert_user_info(user_info)
