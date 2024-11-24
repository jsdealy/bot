import csv, os, string, sqlite3
from datetime import datetime
from .updateFile import updateFile
from .botsay import Botsay
import mechanicalsoup, re


def filmIDSelectSkeleton():
    return "(SELECT id FROM Films WHERE film_name = ?)"

def memberIDSelectSkeleton():
    return "(SELECT id FROM Members WHERE name = ?)"

def wildcardWrapForLIKE(s: str):
    return f"%{s.strip()}%"

async def pick(picker: str, film: str, botsayer: Botsay) -> str:
    if film == "":
        raise Exception("You didn't pick a film!")

    # writing to newfilmdata
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    try:
        # adding a new member if necessary <== 10/07/24 10:20:33 # 
        res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(picker.lower()),))
        result = res.fetchall()
        if len(result) == 0:
            cur.execute("INSERT INTO Members (name) VALUES (?);", (picker.lower(),))
            res = cur.execute("SELECT * FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(picker.lower()),))
            result = res.fetchall()
            if len(result) > 0:
                await botsayer.say(f"Added member: {picker}!")
            else:
                raise Exception("Problem adding a new member!")

        # adding the film <== 10/07/24 10:25:59 # 
        cur.execute("INSERT INTO Films (film_name) VALUES (?);", (film.lower(),))
        res = cur.execute("SELECT * FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(film.lower()),))
        result = res.fetchall()
        if len(result) > 0:
            await botsayer.say(f"Added film data: {string.capwords(film)}!")
        else:
            raise Exception(f"Error: problem adding {film}!")

        # set the picker <== 10/07/24 10:54:55 # 
        dateint = int(datetime.today().strftime("%Y%m%d"))
        cur.execute(f'INSERT INTO Pickers(film_id, user_id, date) VALUES({filmIDSelectSkeleton()},\
            {memberIDSelectSkeleton()}, ?)', (film.lower(), picker.lower(), dateint,))
        res = cur.execute("SELECT * FROM Pickers WHERE date = ?;", (dateint,))
        result = res.fetchall()
        if len(result) > 0:
            await botsayer.say(f"Added picker data: {picker.capitalize()} picked {string.capwords(film)}! :pregnant_man:")
        else:
            raise Exception(f"Problem adding pick: {film}, {picker}!")

        # getting the imdb data <== 11/10/24 10:28:28 # 
        imdb_code = ""
        reg = re.compile(r"tt[0-9]+")
        imdb_url: str = ""
        try:
            try:
                br = mechanicalsoup.StatefulBrowser()
                br.open("http://google.com")
                form = br.select_form()
                form["q"] = f"{film} site:imdb.com"
                form.choose_submit("btnI")
                result = br.submit_selected()
                imdb_url = result.url
            except Exception as e:
                await botsayer.say(f"Problem with fetching imdb data!")
                raise e

            try:
                match_object = reg.search(imdb_url)
                if match_object != None:
                    imdb_code = f"{match_object.group()}"

                    try:
                        cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES ((SELECT id FROM Films WHERE film_name = ?), ?);", (film.lower(),imdb_code))
                        res = cur.execute("SELECT * FROM IMDb_ids WHERE imdb_id = ?;", (imdb_code,))
                        result = res.fetchall()
                        if len(result) > 0:
                            await botsayer.say(f"Added imdb link: [{string.capwords(film)}](http://www.imdb.com/title/{imdb_code})!")
                        else:
                            raise Exception(f"Error: problem adding imdb data for {string.capwords(film)}!")
                    except Exception as e:
                        await botsayer.say(f"Failure inserting imdb data into database!")
                        raise e

            except Exception as e:
                raise e

        except Exception as e:
            con.commit()
            con.close()
            await botsayer.say(f"Error: {e}")
            raise e

    except Exception as e:
        con.commit()
        con.close()
        await botsayer.say(f"Error: {e}")

    con.commit()
    con.close()

    return ""


async def undopick(picker: str, botsayer: Botsay) -> str:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    dateint = int(datetime.today().strftime("%Y%m%d"))
    res = cur.execute(f"SELECT * FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
    results = res.fetchall()
    response = ""
    try:
        if len(results) > 0:
            cur.execute(f"DELETE FROM Films WHERE id IN (SELECT film_id FROM Pickers WHERE date = ? AND user_id = {memberIDSelectSkeleton()})", (dateint,picker,))
            cur.execute(f"DELETE FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
            cur.execute(f"DELETE FROM IMDb_ids WHERE film_id NOT IN (SELECT id FROM Films)")
            res = cur.execute(f"SELECT * FROM Pickers WHERE user_id = {memberIDSelectSkeleton()} AND date = ?", (picker,dateint,))
            results = res.fetchall()
            if len(results) == 0:
                response = "Deleted all your picks from today!"
            else:
                raise Exception("Some kinda problemo deleting picks!")
        else:
            cur.execute(f"DELETE FROM IMDb_ids WHERE film_id NOT IN (SELECT id FROM Films)")
            response = "No picks today to delete! (To delete older picks, contact Justin.)"
    except Exception as e:
        con.commit()
        con.close()
        await botsayer.say(f"Error: {e}")
        raise e

    con.commit()
    con.close()
    return response
