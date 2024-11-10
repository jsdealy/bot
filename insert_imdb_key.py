import sqlite3
from sys import argv


con = sqlite3.connect("filmdata.db")
cur = con.cursor()

try:
    imdb_code = argv[1]
    film_name = str.join(' ',argv[2:]).lower()
    res1 = cur.execute("SELECT id FROM Films WHERE film_name = ?", (film_name,))
    film_id = list(res1.fetchall())[0][0]
    res = cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES (?, ?)", (film_id,imdb_code,))
    con.commit()
    print(f"{film_name}, done")
except Exception as e:
    print(f"Error: {e}")

con.close()

