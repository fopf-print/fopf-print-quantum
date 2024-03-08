import aiogram
import pytest
import mock_bot

from typing import Any

# сомнительно, но окей
from quantum.core import Postgres
from quantum.core.globals import GlobalValue


@pytest.fixture(scope='function', name='db')
def get_db_fixture():
    uri = 'postgresql://fopf:password@127.0.0.1:5432/print'
    return Postgres(uri)


@pytest.fixture(autouse=True, scope='function', name='init_db')
async def init_db_fixture(
        db
):
    DATABASE_INIT_SCRIPT = './db/init_quantum.sql'

    with open(DATABASE_INIT_SCRIPT) as f:
        init_scripts = f.read()

    cleanup_script = '''
    drop schema public cascade;
    create schema public;
    grant all on schema public to fopf;
    grant all on schema public to fopf;
    '''

    await db.execute(cleanup_script)
    await db.execute(init_scripts)


@pytest.fixture(name='create_user')
async def create_user_fixture(
        _id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        balance_cents: int = 0,
):
    await db.execute(
        '''
        insert into users values (?, ?, ?, ?, ?)
        ''',
        [
            _id, first_name, last_name, username, balance_cents
        ]
    )


@pytest.fixture(name='get_default_tg_user')
def default_tg_user_fixture() -> dict[str, Any]:
    return lambda : dict(
        id=1,
        first_name='Марк',
        last_name='Новодачная',
        username='mark_novodachnaya',
        balance_cents=0,
    )


@pytest.fixture(name='create_default_user')
async def create_default_user_fixture(
        create_user,
        get_default_tg_user,
) -> int:
    user = get_default_tg_user()

    await create_user(
        **user()
    )

    return user.id


@pytest.fixture(name='bot')
def bot_fixture(
        get_default_tg_user
):
    GlobalValue[aiogram.Dispatcher].set(
        mock_bot.MockDispatcher
    )

    # тут подтягиваем callback-и
    # сам модуль нам не нужен)
    from quantum import bot
    del bot

    return mock_bot.MockBot(default_user=get_default_tg_user())
