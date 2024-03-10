async def test_bot_start(
        event_loop,
        init_db,
        bot,
):
    _, answer = await bot.command('/start')

    assert answer == ['Зачем ты разбудил меня, смертный?']
