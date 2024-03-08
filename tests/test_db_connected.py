async def test_db(
        db,
):
    r = await db.fetchall('select 123 as abc')

    assert len(r) == 1
    assert 'abc' in r[0]
    assert r[0]['abc'] == 123


async def test_db_initialization(
        db,
):
    # упадёт, если таблы нет
    await db.execute('select * from users')
    assert True


async def test_db_reinitialization(
        db,
):
    # упадёт, если таблы нет
    await db.execute('select * from users')
    assert True
