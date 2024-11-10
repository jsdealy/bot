import mechanicalsoup
br = mechanicalsoup.StatefulBrowser()
google = br.open("http://google.com")
form = br.select_form()
form["q"] = 'bla'
