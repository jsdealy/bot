async def test(message):
    async def botsay(string):
        await message.channel.send(string)
    mess = message.content.lower()
    if mess == "!test":
        await botsay("test passed!")

