async def test_bot_start(
        bot,
):
    response = await bot.command('/start')

    assert response == ['Hello, <b>Марк Новодачная</b>!']


# async def test_get_balance(
#         bot,
#         create_default_user,
# ):
#     user_id = create_default_user()

