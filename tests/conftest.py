import aiogram
import asyncio
import docker
import pytest
import mock_bot

from typing import Any

# сомнительно, но окей
from quantum import settings
from quantum.core import Postgres
from quantum.core.globals import GlobalValue


@pytest.fixture(autouse=True, scope='session', name='pg_container')
async def pg_container_fixture():
    port = 8956
    env = {
        'POSTGRES_DB': 'print',
        'POSTGRES_USER': 'fopf',
        'POSTGRES_PASSWORD': 'fopf',
    }

    client = docker.from_env()
    postgres_container = client.containers.run(
        'postgres:16',
        environment=env,
        ports={5432: port},
        detach=True,
    )

    await asyncio.sleep(5)

    if postgres_container.status != 'created':
        raise RuntimeError('smth wrong with docker container')

    yield postgres_container  # вообще тут можно что угодно

    postgres_container.stop()
    postgres_container.remove()


@pytest.fixture(scope='function', name='db')
def get_db_fixture(
        pg_container
):
    return Postgres(settings.POSTGRES_CONNECTION_URI)


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
