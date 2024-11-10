import sqlite3
from sys import argv


con = sqlite3.connect("filmdata.db")
cur = con.cursor()

try:
    imdb_code = argv[1]
    print(imdb_code, str.join(' ',argv[2:]).lower())
    # res = cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES (?, ?)", (film_tup[1],imdb_code,))
    # con.commit()
    # print(f"{film_tup[0]}, done")
except Exception as e:
    print(f"Error: {e}")

con.close()

