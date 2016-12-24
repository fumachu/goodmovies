import urllib
import BeautifulSoup

class IMDBLists:

    def load_top_250(self):
        imdb_top_250_url = urllib.urlopen("http://www.imdb.com/chart/top?lang=en")
        imdb_top_250_html = imdb_top_250_url.read()
        soup = BeautifulSoup.BeautifulSoup(imdb_top_250_html)
        IMDBTableBody = soup.find('tbody',{'class': 'lister-list'})
        filmTitleLines = IMDBTableBody.findAll('td', {'class': 'titleColumn'})

        films = []

        for eachFilmLine in filmTitleLines:
            filmLink = eachFilmLine.find('a')
            films.append(filmLink.text)

        return films

def IMDBAccess():
    return IMDBLists()
