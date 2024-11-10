import mechanicalsoup,sqlite3,re
from mechanicalsoup import Form

br = mechanicalsoup.StatefulBrowser()
google = br.open("http://www.imdb.com")
form: Form = br.select_form()
form.print_summary()
# form["q"] = f"{film_tup[0]} site:imdb.com"
# form.choose_submit("btnI")
# response = br.submit_selected()
