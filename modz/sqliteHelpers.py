import sqlite3,string
from datetime import datetime

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

def getMembers() -> list[str]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM Members;")
    names_raw = res.fetchall()
    con.close()
    if len(names_raw) > 0:
        return list(x[0] for x in names_raw)
    else:
        raise Exception("Problem getting members!")


def getFilmsLIKE(s: str):
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

def getUserID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    user_id = res.fetchone()[0]
    con.close()
    return user_id

    
