import sqlite3,string
from datetime import datetime
from typing import Any, List

class FDCon:
    def __init__(self) -> None:
        self._con = sqlite3.connect("filmdata.db")
        self._cur = self._con.cursor()
    def __del__(self):
        self._con.close()
    def cur(self) -> sqlite3.Cursor:
        return self._cur
    def execute(self,sql_string: str):
        return self._cur.execute(sql_string)
    def commit(self):
        return self._con.commit()

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

def delete(cur: sqlite3.Cursor, table: str, **values: Any) -> bool:
    """
    File: sqliteHelpers.py
    Author: Justin Dealy
    Github: https://github.com/jsdealy
    Description: Deletes from a table. Values 
    cannot be empty. Does not commit changes.
    """
    cur.fetchall()
    if len(values) < 1:
        raise Exception("Called delete without any values")
    list_of_fields: list[str] = [key for key in values.keys()]
    field_string_list = [f"{field}=?" for field in list_of_fields]
    list_of_values = [values[key] for key in list_of_fields]
    field_list_str = f"({' AND '.join(field_string_list)})"
    val_tup = tuple(list_of_values)
    try:
        cur.execute(f"DELETE FROM {table} WHERE {field_list_str};", val_tup)
    except Exception as e:
        print(f"Error: {e}")
        raise e
    return True

def insert(cur: sqlite3.Cursor, table: str, **values: Any) -> bool:
    """
    File: sqliteHelpers.py
    Author: Justin Dealy
    Github: https://github.com/jsdealy
    Description: Inserts into sqlite table in database associated with 
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

def select(cur: sqlite3.Cursor, *selected_cols: str, **values: Any) -> list[tuple[Any]]:
    """
    File: sqliteHelpers.py
    Author: Justin Dealy
    Github: https://github.com/jsdealy
    Description: Selects from sqlite tables associated with 
    cursor. selected_cols is what it sounds like.
    One of the values must have the key "tables". 
    Optionally, one of the values can be "join".
    The rest should have keys that are columnnames 
    and values being whatever you want to select. 
    Double underscores in columnnames are replaced 
    with a period. Returns raw list of tuples.
    """
    if "tables" not in values.keys() or not isinstance(values["tables"],List):
        raise Exception("Call to select did not include a list value for arg 'tables'.")
    cur.fetchall()
    table_list = values.pop("tables")
    join_table = []
    if "joins" in values.keys():
        join_table = values.pop("joins")
    list_of_fields: list[str] = [f"{key.replace("__",".")}=?" for key in values.keys()]
    list_of_values = [values[key] for key in values.keys()]
    table_list_str = f"{', '.join(table_list)}"
    selected_cols_str = f"{', '.join(selected_cols)}"
    field_list_str = f"{' AND '.join(join_table + list_of_fields)}"
    val_tup = tuple(list_of_values)
    # print(f"SQL STRING: SELECT {selected_cols_str} FROM {table_list_str} WHERE {field_list_str};")
    # print(val_tup)
    try:
        raw_tups = cur.execute(f"SELECT {selected_cols_str} FROM {table_list_str} WHERE {field_list_str};", val_tup).fetchall()
        return raw_tups
    except Exception as e:
        print(f"Error: {e}")
        raise e

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

def getOrCreateAndGetUserID(username: str, _retry=False) -> int:
    """
    File: sqliteHelpers.py
    Author: Justin Dealy
    Email: yourname@email.com
    Github: https://github.com/yourname
    Description: Tries to get the user_id of username.
    If the try fails, tries to insert username as a 
    new entry in Members. Retry is used for recursion
    and should be left False in non-recursive calls.
    """
    
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    user_id: int = -1
    try: 
        user_id = cur.execute("SELECT id FROM Members WHERE name LIKE ?;", (wildcardWrapForLIKE(username.lower()),)).fetchone()[0]
    except Exception as e:
        print(f"Error: {e}")
        if _retry:
            raise e
        try:
            insert(cur,"Members",name=username)
            con.commit()
        except Exception as e:
            print(f"Error: {e}")
            raise e
        getOrCreateAndGetUserID(username, True)
    con.close()
    return user_id
