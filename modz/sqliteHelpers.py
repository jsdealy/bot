import sqlite3,string
from datetime import datetime
from .botsay import Botsay
from .newIMDb import addIMDbData
from typing import Any

def filmIDSelectSkeleton():
    return "(SELECT id FROM Films WHERE film_name = ?)"

def memberIDSelectSkeleton():
    return "(SELECT id FROM Members WHERE name = ?)"

def wildcardWrapForLIKE(s: str | list[str]):
    if isinstance(s, str):
        return f'%{s.strip()}%'
    else:
        return f'%{"%".join(s)}%'

def today():
    return int(datetime.today().strftime("%Y%m%d"))

def insert(cur: sqlite3.Cursor, table: str, **values: Any) -> bool:
    cur.fetchall()
    list_of_fields: list[str] = [key for key in values.keys()]
    list_of_qmarks = ["?" for key in list_of_fields]
    list_of_values = [values[key] for key in list_of_fields]
    field_list_str = f"({', '.join(list_of_fields)})"
    qmark_list_str = f"({', '.join(list_of_qmarks)})"
    val_tup = tuple(list_of_values)
    try:
        cur.execute(f"INSERT INTO {table} {field_list_str} VALUES {qmark_list_str};", val_tup)
    except Exception as e:
        print(f"Error: {e}")
        raise e
    list_of_equations = [f"{key}={values[key]}" for key in list_of_fields]
    cur.execute(f"SELECT * FROM {table} WHERE {' AND '.join(list_of_equations)};")
    if len(cur.fetchall()) < 1:
        print(f"Failed to add {' AND '.join(list_of_equations)} to {table}.")
        return False
    return True

async def insertIntoUserList(user: str, film: str, **kwargs: Botsay) -> None:
    doprint = False
    botsayer = kwargs.get("botsayer")
    if "botsayer" in kwargs.keys():
        doprint = True
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    film_id: int = 0
    cur.execute("SELECT * FROM Members WHERE name = ?;", (user.lower(),))
    if len(cur.fetchall()) < 1:
        if insert(cur, "Members", name=user.lower()) and doprint:
            print(f"Added member {user}!") 
            await botsayer.say(f"Added member {user}!") 
        else:
            raise Exception(f"Couldn't add member {user}")
    user_id: int = cur.execute("SELECT id FROM Members WHERE name = ?", (user.lower(),)).fetchall()[0][0]
    cur.execute("SELECT * FROM Films WHERE film_name = ?;", (film.lower(),))
    if len(cur.fetchall()) < 1:
        if insert(cur, "Films", film_name=film.lower()):
            print(f"Added film to database: {film.lower()}!")
        else:
            raise Exception(f"Couldn't add film to database: {film.lower()}")
        film_id = cur.execute("SELECT id FROM Films WHERE film_name = ?", (film.lower(),)).fetchall()[0][0]
        try:
            addIMDbData(film_id)
        except Exception as e:
            raise e
        print(f"Added IMDb data for {film.lower()}")
    cur.execute("SELECT * FROM Lists WHERE film_id = ? AND user_id = ?", (film_id, user_id,))
    if len(cur.fetchall()) < 1:
        if insert(cur, "Lists", film_id=film_id, user_id=user_id):
            print(f"Added {film} to {user}'s list.")
        else:
            raise Exception(f"Couldn't add {film} to {user}'s list.")
    elif doprint:
        print(f"{film} is already in {user}'s list!")
        await botsayer.say(f"{film} is already in {user}'s list!")
    con.close()

def getMembers() -> list[str]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM Members;")
    names_raw = res.fetchall()
    con.close()
    if len(names_raw) > 0:
        return list(x[0] for x in names_raw)
    else:
        raise Exception("Didn't find any members in database, oh no!")

def getAllFilms() -> list[str]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films;")
    films_raw = res.fetchall()
    con.close()
    if len(films_raw) > 0:
        return [tup[0] for tup in films_raw]
    else:
        raise Exception("Didn't find any films in database, oh no!")

def getIMDbForFilmLIKE(s: str) -> str:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT imdb_id FROM Films, IMDb_ids WHERE Films.id = IMDb_ids.film_id AND Films.film_name LIKE ?;", (wildcardWrapForLIKE(s),))
    imdb_id = res.fetchall()[0][0]
    con.close()
    return imdb_id

def getFilmsLIKE(s: str) -> list[tuple[str]]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s.replace("'",'%').lower()),))
    films = res.fetchall()
    con.close()
    return films

def getFilmIDs(s: str) -> list[tuple[int]]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s.replace("'",'%').lower()),))
    film_ids = res.fetchall() 
    con.close()
    return film_ids

def getFilmID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s.replace("'",'%').lower()),))
    film_ids = res.fetchall()
    con.close()
    if len(film_ids) > 0:
        film_id = film_ids[0][0]
        return film_id
    else:
        raise Exception(f"Film '{string.capwords(s)}' not found in database.")

def getRating(user_id: int, film_id: int) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT rating FROM Ratings WHERE film_id = ? AND user_id = ?;", (film_id,user_id,))
    ratings = res.fetchall()
    con.close()
    if len(ratings) > 0:
        rating = ratings[0][0]
        return rating
    else:
        raise Exception(f"Problem fetching rating for user_id {user_id} and film_id {film_id}.")

def getUserID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    user_id = res.fetchone()[0]
    con.close()
    return user_id
