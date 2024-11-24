import mechanicalsoup,sqlite3,re
from sys import argv

def addIMDbData(film_id: int):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name FROM Films WHERE id = ?;", (film_id,))
    films_raw = res.fetchall()
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
        con.commit()
        print(f"{film_name}, done")
    except Exception as e:
        print(f"Error: {e}")
    con.close()

