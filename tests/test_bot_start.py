async def test_bot_start(
        bot,
):
    _, answer = await bot.command('/start')

    assert answer == ['Hello, <b>Марк Новодачная</b>!']
