import asyncio
import pytest

from quantum.core import db


@pytest.fixture(autouse=True, name='init_db')
async def init_db_fixture():
    DATABASE_INIT_SCRIPT = './db/init_quantum.sql'

    with open(DATABASE_INIT_SCRIPT) as f:
        init_scripts = f.read()

    await asyncio.gather(
        *(db.execute(script) for script in init_scripts.split(';'))
    )
