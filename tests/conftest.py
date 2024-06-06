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
    return Postgres(settings.postgres_connection_uri)


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


@pytest.fixture(autouse=True, name='create_user')
async def create_user_fixture(
        db,
):
    async def inner(
            id: int,
            first_name: str | None = None,
            last_name: str | None = None,
            username: str | None = None,
            balance_cents: int = 0,
    ):
        await db.execute(
            '''
            insert into users values ($1, $2, $3, $4, $5)
            ''',
            [
                id, first_name, last_name, username, balance_cents
            ]
        )
    return inner


@pytest.fixture(scope='session', name='get_default_tg_user')
def default_tg_user_fixture():
    return lambda: dict(
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
):
    async def inner():
        user = get_default_tg_user()

        await create_user(
            **user
        )

        return user['id']
    return inner


@pytest.fixture(scope='session', name='bot')
def bot_fixture(
        get_default_tg_user
):
    GlobalValue[aiogram.Dispatcher].set(
        mock_bot.MockDispatcher
    )

    mbot = mock_bot.MockBot(default_user=get_default_tg_user())
    GlobalValue[aiogram.Bot].set(mbot)

    # тут подтягиваем callback-и
    # сам модуль нам не нужен)
    from quantum import bot
    del bot

    return mbot


@pytest.yield_fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
