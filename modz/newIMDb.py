import mechanicalsoup,sqlite3,re
from sys import argv


con = sqlite3.connect("filmdata.db")
cur = con.cursor()
res = cur.execute("SELECT film_name, id FROM Films;")
films_raw = res.fetchall()

reg = re.compile(r"tt[\d]+")

for film_tup in films_raw:
    br = mechanicalsoup.StatefulBrowser()
    google = br.open("http://google.com")
    form = br.select_form()
    form["q"] = f"{film_tup[0]} site:imdb.com"
    form.choose_submit("btnI")
    response = br.submit_selected()
    reg_match = reg.search(response.url)
    try:
        imdb_code = reg_match.group()
        res = cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES (?, ?)", (film_tup[1],imdb_code,))
        con.commit()
        print(f"{film_tup[0]}, done")
    except Exception as e:
        print(f"Error: {e}")

con.close()

