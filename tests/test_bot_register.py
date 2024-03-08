async def test_bot_register__unidentified(
        init_db,
        bot,
):
    _, answer = await bot.command(
        '/register',
        from_user=None,
    )

    assert answer == [
        "Got some errors: ['USER_IS_UNIDENTIFIED']",
    ]


async def test_bot_register__success(
        init_db,
        bot,
        get_default_tg_user,
        db,
):
    reply, _ = await bot.command('/register')

    assert reply == [
        'Done!)',
    ]

    user_info = get_default_tg_user()

    db_user = await db.fetchall('select * from users')

    assert db_user == [user_info]
