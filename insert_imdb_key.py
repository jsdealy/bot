import sqlite3
from modz.sqliteHelpers import wildcardWrapForLIKE
from sys import argv


con = sqlite3.connect("filmdata.db")
cur = con.cursor()

try:
    imdb_code = argv[1]
    film_name_list = [x.lower().replace(',','').replace('"','') for x in argv[2:]]
    res1 = cur.execute("SELECT id FROM Films WHERE film_name LIKE ?", (wildcardWrapForLIKE(film_name_list),))
    film_id = list(res1.fetchall())[0][0]
    res = cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES (?, ?)", (film_id,imdb_code,))
    con.commit()
    print(f"{' '.join(film_name_list)}, done")
except Exception as e:
    print(f"Error: {e}")

con.close()

