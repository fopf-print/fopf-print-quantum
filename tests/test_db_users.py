from quantum.entities import users
from quantum.connectors import db_users

async def test_create_user_then_fetch(
        init_db
):
    user_id = 123456

    test_user = users.User(
        id=user_id,
        first_name='first name',
        last_name='second name',
        username='username',
        balance_cents=0,
    )

    await db_users.upsert_user_info(test_user)

    user_from_db = await db_users.get_user_info(user_id)

    assert test_user.model_dump_json() == user_from_db.model_dump_json()
