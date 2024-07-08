import csv, os, string
from .updateFile import updateFile

async def pick(picker, members, film, botsay, tryprint, fieldnames, guild, channel, memberIDs):
    tryprint(film)
    if film == "":
        await botsay("You didn't pick a film!", channel)
        return

    await botsay("*Determining the new queue...*", channel)

    current = []
    with open("rotation.csv", "r") as rob:
        reader = csv.reader(rob)
        current = next(reader)

    # building the rotation
    tmp = []
    for j in range(len(current)):
        if current[j] != picker:
            tmp += [current[j]] 
    tmp += [picker]
    tryprint(f"tmp = {tmp}")

    await botsay("*Updating the rotation database...*", channel)

    # updating the rotation file
    with open("newrotation.csv", "w") as fob2, open("rotation.csv", "r") as rob:
        writer = csv.writer(fob2)
        writer.writerow(tmp)
        reader = csv.reader(rob)
        writer.writerow(next(reader))

    await updateFile(tryprint, "newrotation.csv", "rotation.csv")

    await botsay("*Creating a new film entry for the database...*", channel)

    # creating the new filmdata dictionary ("line" for the filmdata csv)
    newDict = {}
    newDict = { 
                   "film": f"{film}",
                   "picker": f"{picker}",
                   "justin": "0",
                   "tim": "-1",
                   "louis": "0",
                   "patrick": "0",
              }
    tryprint(f"newDict = {newDict}")
    
    await botsay("*Writing the data...*", channel)

    # writing to newfilmdata
    try:
        with open("filmdata.csv", "r") as rdata, open("newfilmdata.csv", "w") as fob3:
            reader = csv.DictReader(rdata)
            writer = csv.DictWriter(fob3, fieldnames=fieldnames)
            writer.writeheader()
            for readrow in reader:
                writer.writerow(readrow)
            writer.writerow(newDict)
    except:
        await botsay("Problem opening and editing filmdata.", channel)

    # replacing old filmdata with newfilmdata
    await updateFile(tryprint, "newfilmdata.csv", "filmdata.csv")

    # sending a response to the chat
    response = ""
    response = f"\n**The film this week is {string.capwords(newDict['film'])}.**\n"
    response += f"**{tmp[0].title()} is now next in line to choose a film.**"
    await botsay(response, channel)
    await botsay("*All done!* :pregnant_man:", channel)

async def undopick(picker,
                     members,
                     botsay,
                     tryprint,
                     fieldnames,
                     guild,
                     channel,
                   memberIDs):
    # checking whether there are 
    # two rows in rotation, and if so 
    # reading current and old rotation into lists 
    old = []
    try:
        with open("rotation.csv", "r") as rob:
            reader = csv.reader(rob)
            current = next(reader)
            old = next(reader)
    except:
        await botsay("Looks like someone has already undone a pick!", channel)
        tryprint("Failed attempt to undo a pick; only one row in rotation.csv.")
        return

    # building a filmdata list of dicts that deletes the last row
    # currently in filmdata
    filmdata = []
    with open ("filmdata.csv", "r") as rob:
        reader = csv.DictReader(rob)
        for row in reader:
            filmdata += [row]
    lastfilmrow = filmdata[len(filmdata)-1]
    tryprint(f"most recent film = {lastfilmrow['film']}")

    # blocking undo in certain cases
    if lastfilmrow['picker'] != picker:
        await botsay("You can't undo the most recent pick, since you didn't pick it, you silly goose!", channel)
        return
    for name in members:
        if int(lastfilmrow[name]) > 0:
            await botsay("You can't undo the most recent pick, since people have already rated it!", channel)
            return

    # removing the most recent row from filmdata.csv
    with open("newfilmdata.csv", "w") as wob: 
        writer = csv.DictWriter(wob, fieldnames=fieldnames)
        writer.writeheader()
        for row in filmdata[:len(filmdata)-1]:
            writer.writerow(row)
    try:
        os.replace("newfilmdata.csv", "filmdata.csv")
        tryprint("Most recent row removed from film data.")
        await botsay(f"{string.capwords(lastfilmrow['film'])} has been removed from the film database.", channel)
    except:
        tryprint("Removal of most recent film row failed due to OS error.")

    await botsay("*Fixing the rotation data...*", channel)
    # updating the rotation file
    with open("newrotation.csv", "w") as fob2, open("rotation.csv", "r") as rob:
        writer = csv.writer(fob2)
        reader = csv.reader(rob)
        # discarding the first row of rotation
        next(reader)
        writer.writerow(next(reader))

    await updateFile(tryprint, "newrotation.csv", "rotation.csv", "*All done!* :whale:", botsay, channel)


async def pickSystem(author, members, mess, usernames, botsay, tryprint, fieldnames, guild, channel, memberIDs):

    # undoing a pick 
    for i in range(len(members)):
        if (author.id == memberIDs[members[i]] and mess.startswith('undopick')) or (author.id == memberIDs["justin"] and mess.startswith(f"undo{members[i]}pick")):
            await undopick(members[i], members, botsay, tryprint, fieldnames, guild, channel, memberIDs)

    # making a pick
    for i in range(len(members)):
        if (author.id == memberIDs[members[i]] and mess.startswith('pick:')) or (author.id == memberIDs["justin"] and mess.startswith(f"{members[i]}pick:")):
            film = f"{mess.removeprefix(members[i]).removeprefix('pick:').removesuffix('*').strip()}"
            await pick(members[i], members, film, botsay, tryprint, fieldnames, guild, channel, memberIDs)
