async def test_bot_start(
        init_db,
        bot,
):
    _, answer = await bot.command('/start')

    assert answer == ['Hello, <b>Марк Новодачная</b>!']
