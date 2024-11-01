import sqlite3
from datetime import datetime

def filmIDSelectSkeleton():
    return "(SELECT id FROM Films WHERE film_name = ?)"

def memberIDSelectSkeleton():
    return "(SELECT id FROM Members WHERE name = ?)"

def wildcardWrapForLIKE(s: str):
    return f'%{s.strip()}%'

def today():
    return int(datetime.today().strftime("%Y%m%d"))

def getFilmsLIKE(s: str):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s[:s.find("'")].lower()),))
    films = res.fetchall()
    con.close()
    return films

def getFilmIDs(s: str) -> list[tuple[int]]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s[:s.find("'")].lower()),))
    film_ids = res.fetchall() 
    con.close()
    return film_ids

def getFilmID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s[:s.find("'")].lower()),))
    film_ids = res.fetchall()
    con.close()
    if len(film_ids) > 0:
        film_id = film_ids[0][0]
        return film_id
    else:
        raise Exception("Film not found.")

def getUserID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    user_id = res.fetchone()[0]
    con.close()
    return user_id

    
