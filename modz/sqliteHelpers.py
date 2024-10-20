import sqlite3
from datetime import datetime

def filmIDSelectSkeleton():
    return "(SELECT id FROM Films WHERE film_name = ?)"

def memberIDSelectSkeleton():
    return "(SELECT id FROM Members WHERE name = ?)"

def wildcardWrapForLIKE(s: str):
    return f"%{s.strip()}%"

def today():
    return int(datetime.today().strftime("%Y%m%d"))

def getFilmsLIKE(s: str):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    con.close()
    return res.fetchall()

def getFilmID(s: str) -> list[tuple[int]]:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    con.close()
    return res.fetchall()

def getUserID(s: str) -> int:
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(s.lower()),))
    con.close()
    return res.fetchone()[0]

    
