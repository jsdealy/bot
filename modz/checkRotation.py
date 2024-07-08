import csv

turns = [ "next", "second in line", "third in line", "fourth in line" ]

async def checkRotation(mess, members, botsay, tryprint, channel):
    # reporting a member's POSITION in the rotation
    for i in range(len(members)):
        if mess.rstrip("!?.") == f'{members[i]}check':
            response = f"{members[i].title()} is {turns[i]}."
            await botsay(response, channel)


    # reporting the FULL current rotation
    if mess == 'check!':
        current = []
        with open("rotation.csv") as ob:
            reader = csv.reader(ob)
            current = next(reader)
        res = f"Currently "
        tryprint(res)
        for i in range(len(current)-1):
            res += f"{current[i].title()} is {turns[i]}, "
        res += f"and {current[len(current)-1].title()} is {turns[len(current)-1]}."
        await botsay(res, channel)
