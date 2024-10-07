import csv, os, string, sqlite3
from datetime import datetime
from .updateFile import updateFile

async def pick(picker: str, film: str, botsay, tryprint, channel):
    tryprint(film)
    if film == "":
        await botsay("You didn't pick a film!", channel)
        return

    await botsay("*Creating a new film entry for the database...*", channel)

    # writing to newfilmdata
    try:
        con = sqlite3.connect("filmdata.db")
        cur = con.cursor()

        # adding a new member if necessary <== 10/07/24 10:20:33 # 
        res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (picker.lower(),))
        result = res.fetchall()
        if len(result) == 0:
            cur.execute("INSERT INTO Members (name) VALUES (?);", (picker.lower(),))
            res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (picker.lower(),))
            result = res.fetchall()
            if len(result) > 0:
                await botsay(f"Added member: {picker}!")
            else:
                raise Exception("Problem adding a new member!")

        # adding the film <== 10/07/24 10:25:59 # 
        cur.execute("INSERT INTO Films (film_name) VALUES (?);", (film.lower(),))
        res = cur.execute("SELECT * FROM Films WHERE film_name LIKE ?;", (film.lower(),))
        result = res.fetchall()
        if len(result) > 0:
            await botsay(f"Added film to main list: {film}!", channel)
        else:
            raise Exception(f"Problem adding {film}!")


        # set the picker <== 10/07/24 10:54:55 # 
        dateint = int(datetime.today().strftime("%Y%m%d"))
        cur.execute(f'INSERT INTO Pickers(film_id, user_id, date) VALUES((SELECT id FROM Films WHERE film_name = ?),\
        (SELECT id FROM Members WHERE name = ?), ?)', (film.lower(), picker.lower(), dateint,))
        res = cur.execute("SELECT * FROM Pickers WHERE date = ?;", (dateint,))
        result = res.fetchall()
        if len(result) > 0:
            await botsay(f"Added picker: {picker}!", channel)
        else:
            raise Exception(f"Problem adding pick: {film}, {picker}!")

        # committing the changes <== 10/07/24 12:39:04 # 
        con.commit()
            
    except Exception as e:
        await botsay(f"Error: {e}", channel)
        raise e

    # sending a response to the chat
    # response += f"**{} is now next in line to choose a film.**"
    # await botsay(response, channel)
    # await botsay("*All done!* :pregnant_man:", channel)

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
    # for i in range(len(members)):
    #     if (author.id == memberIDs[members[i]] and mess.startswith('undopick')) or (author.id == memberIDs["justin"] and mess.startswith(f"undo{members[i]}pick")):
    #         await undopick(members[i], members, botsay, tryprint, fieldnames, guild, channel, memberIDs)

    # making a pick
    if (mess.startswith('pick:')):
        film = f"{mess.removeprefix('pick:').removesuffix('*').strip()}"
        await pick(author, film, botsay, tryprint, channel)
