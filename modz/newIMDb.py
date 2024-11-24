import mechanicalsoup,sqlite3,re

def addIMDbData(cur: sqlite3.Cursor, film_id: int):
    res = cur.execute("SELECT film_name FROM Films WHERE id = ?;", (film_id,))
    films_raw = res.fetchall()
    print(films_raw, film_id)
    film_name = films_raw[0][0]
    reg = re.compile(r"tt[\d]+")
    br = mechanicalsoup.StatefulBrowser()
    br.open("http://google.com")
    form = br.select_form()
    form["q"] = f"{film_name} site:imdb.com"
    form.choose_submit("btnI")
    response = br.submit_selected()
    reg_match = reg.search(response.url)
    try:
        imdb_code = reg_match.group()
        res = cur.execute("INSERT INTO IMDb_ids (film_id, imdb_id) VALUES (?, ?)", (film_name,imdb_code,))
        print(f"{film_name}, done")
    except Exception as e:
        print(f"Error: {e}")

