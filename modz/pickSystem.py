import csv, os, string, sqlite3
from datetime import datetime
from .updateFile import updateFile

def filmIDSelectSkeleton():
    return "(SELECT id FROM Films WHERE film_name = ?)"

def memberIDSelectSkeleton():
    return "(SELECT id FROM Members WHERE name = ?)"

def wildcardWrapForLIKE(s: str):
    return f"%{s.strip()}%"

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
        res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(picker.lower()),))
        result = res.fetchall()
        if len(result) == 0:
            cur.execute("INSERT INTO Members (name) VALUES (?);", (picker.lower(),))
            res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(picker.lower()),))
            result = res.fetchall()
            if len(result) > 0:
                await botsay(f"Added member: {picker}!")
            else:
                raise Exception("Problem adding a new member!")

        # adding the film <== 10/07/24 10:25:59 # 
        cur.execute("INSERT INTO Films (film_name) VALUES (?);", (film.lower(),))
        res = cur.execute("SELECT * FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(film.lower()),))
        result = res.fetchall()
        if len(result) > 0:
            await botsay(f"Added film data: {film}!", channel)
        else:
            raise Exception(f"Problem adding {film}!")


        # set the picker <== 10/07/24 10:54:55 # 
        dateint = int(datetime.today().strftime("%Y%m%d"))
        cur.execute(f'INSERT INTO Pickers(film_id, user_id, date) VALUES({filmIDSelectSkeleton()},\
            {memberIDSelectSkeleton()}, ?)', (film.lower(), picker.lower(), dateint,))
        res = cur.execute("SELECT * FROM Pickers WHERE date = ?;", (dateint,))
        result = res.fetchall()
        if len(result) > 0:
            await botsay(f"Added picker data: {picker.capitalize()} picked {film}! :pregnant_man:", channel)
        else:
            raise Exception(f"Problem adding pick: {film}, {picker}!")

        # committing the changes and closing the connection <== 10/07/24 12:39:04 # 
        con.commit()
        con.close()
            
    except Exception as e:
        await botsay(f"Error: {e}", channel)
        raise e

    # sending a response to the chat
    # response += f"**{} is now next in line to choose a film.**"
    # await botsay(response, channel)
    # await botsay("*All done!* :pregnant_man:", channel)

async def undopick(picker,
                     botsay,
                     tryprint,
                     channel):

    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    dateint = int(datetime.today().strftime("%Y%m%d"))
    res = cur.execute(f"SELECT * FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
    results = res.fetchall()
    if len(results) > 0:
        try:
            cur.execute(f"DELETE FROM Films WHERE id IN (SELECT film_id FROM \
            Pickers WHERE date = ? AND user_id = {memberIDSelectSkeleton()})", (dateint,picker,))
            cur.execute(f"DELETE FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
            res = cur.execute(f"SELECT * FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
            results = res.fetchall()
            if len(results) == 0:
                tryprint("Deleted picks.")
                await botsay("Deleted all your picks from today!", channel)
            else:
                raise Exception("Some kinda problemo deleting picks!")
        except Exception as e:
            await botsay(f"Error: {e}", channel)
            raise e
    else:
        await botsay("No picks today to delete! (To delete older picks, contact Justin.)", channel)

    con.commit()
    con.close()



async def pickSystem(author, members, mess, usernames, botsay, tryprint, fieldnames, guild, channel, memberIDs):

    # undoing a pick 
    
    if mess.startswith('undopick'):
        await undopick(author, botsay, tryprint, channel)

    # making a pick
    if mess.startswith('pick:'):
        film = f"{mess.removeprefix('pick:').strip()}"
        await pick(author, film, botsay, tryprint, channel)
