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
    """
    File: sqliteHelpers.py
    Author: Justin Dealy
    Github: https://github.com/jsdealy
    Description: Inserts into sqlite table associated with 
    cursor. Values are named arguments where name is 
    the columnname and value is whatever you want to insert. 
    Does not commit the result. 
    """
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
    return True

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

def getAllPicks() -> list[str]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films, Pickers WHERE Films.id = Pickers.film_id;")
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

def getUserID(username: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(username.lower()),))
    user_id = res.fetchone()[0]
    con.close()
    return user_id

def getOrCreateAndGetUserID(username: str, retry=False) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    user_id: int = -1
    try: 
        user_id = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(username.lower()),)).fetchone()[0]
    except Exception as e:
        print(f"Error: {e}")
        if retry:
            raise e
        insert(cur,"Members",name=username)
        con.commit()
        getOrCreateAndGetUserID(username, True)
    con.close()
    return user_id
