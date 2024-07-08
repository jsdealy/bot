import csv, string
from .numToRating import numToRating
from .members import members

async def listPicks(picker, botsay, channel):
    response = f"{picker.upper()}'S PICKS\n\n"
    with open("filmdata.csv", "r") as rob:
        reader = csv.DictReader(rob)
        for row in reader:
            if row['picker'] == picker:
                response += f"{string.capwords(row['film'])}\n"
    await botsay(response, channel)

def retIndexTwo(lst):
    return lst[1]

async def memberSeenAndPick(mess, botsay, channel):
    # print movies member has seen
    for i in range(len(members)):
        if mess.rstrip("!?") == f"{members[i]}seen":
            response = ""
            lst = []
            with open("filmdata.csv", "r") as rob:
                reader = csv.DictReader(rob)
                for row in reader:
                    if int(row[members[i]]) >= 0:
                        lst += [[row['film'], int(row[members[i]])]]
                lst.sort(key=retIndexTwo, reverse=True)
                for j in range(len(lst)):
                    response += f"{string.capwords(lst[j][0])}: {numToRating(int(lst[j][1])).title()}\n"
            await botsay(response, channel)
            break

    # print movies member has not seen
    for i in range(len(members)):
        if mess.rstrip("?!") == f"{members[i]}notseen":
            response = ""
            with open("filmdata.csv", "r") as rob:
                reader = csv.DictReader(rob)
                for row in reader:
                    if int(row[members[i]]) < 0:
                        response += f"{string.capwords(row['film'])}\n"
            await botsay(response, channel)
            break

    # listing member's picks
    for i in range(len(members)):
        if mess.startswith(f"{members[i]}picks"):
            await listPicks(members[i], botsay, channel)
