import string

async def botsay(string, channel):
    await channel.send(string)

async def botsaylist(list, channel):
    response = ""
    for s in list:
        response += string.capwords(s)+'\n'
    await botsay(response, channel)
