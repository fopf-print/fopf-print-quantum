async def test_bot_register__unidentified(
        event_loop,
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


async def test_bot_register__already_registered(
        init_db,
        bot,
        create_default_user,
        db,
):
    await create_default_user()
    reply, _ = await bot.command('/register')

    assert reply == ['ты уже смешарик']

