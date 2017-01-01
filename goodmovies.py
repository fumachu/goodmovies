import argparse
import io
import urllib2
import logging
from bs4 import BeautifulSoup, SoupStrainer

class IMDBScraper:
    __language = "en-US"
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('goodmovies')

    def setLanguage(self,language):
        self.__language = language

    def loadTop250(self):
        IMDBResponseAsString = self.__fetchIMDBSiteContent("http://www.imdb.com/chart/top")

        strainer = SoupStrainer('td', attrs={'class': 'titleColumn'})
        soup = BeautifulSoup(IMDBResponseAsString, 'lxml', parse_only=strainer)
        movieTitleLines = soup.findAll('td', {'class': 'titleColumn'})

        movies = []

        for eachMovieLine in movieTitleLines:
            movieLink = eachMovieLine.find('a')
            movies.append(movieLink.text)

        return movies

    def loadTopMoviesByGenre(self,imdbGenreKey,count):
        movies = []

        currentPage = 1

        while True:
            IMDBGenreURL = "http://www.imdb.com/search/title?genres=" + imdbGenreKey + "&sort=user_rating,desc&title_type=feature&num_votes=25000,&view=simple&page=" + str(currentPage)

            IMDBResponseAsString = self.__fetchIMDBSiteContent(IMDBGenreURL)

            strainer = SoupStrainer('span', attrs={'class': 'lister-item-header'})
            soup = BeautifulSoup(IMDBResponseAsString, 'lxml', parse_only=strainer)
            movieTitleLines = soup.findAll('span', {'class': 'lister-item-header'})

            if len(movieTitleLines) == 0:
                self.__logger.error('Did not get results parsing result for URL "%s", aborting',IMDBGenreURL)
                break

            for eachMovieLine in movieTitleLines:
                movieLink = eachMovieLine.find('a')
                movies.append(movieLink.text)

            if len(movies) >= count:
                break

            currentPage += 1

        return movies

    def __fetchIMDBSiteContent(self,url):
        # upon sending a request from IMDB with header 'Accept-Language'
        # IMDB will return the site and the move titles in this language
        IMDBRequest = urllib2.Request(url, "",
            { "Accept-Language" : self.__language })

        IMDBResponse = urllib2.urlopen(IMDBRequest)
        IMDBResponseAsString = IMDBResponse.read()

        return IMDBResponseAsString

class GoodMoviesRunner:
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('goodmovies')

    def execute(self):
        commandLineArguments = self.__parseCommandLineArguments()

        self.__initLogging(commandLineArguments)

        self.__logger.info('GoodMovies started')

        moviesThatShouldBeInFile = self.__readMoviesThatShouldBeInFile(commandLineArguments)
        moviesAlreadyInFile = self.__readMoviesAlreadyInFile(commandLineArguments)
        moviesToInsertIntoFile = self.__findMoviesToInsertIntoFile(moviesAlreadyInFile,moviesThatShouldBeInFile)

        if commandLineArguments.outputfile != '':
            self.__insertMoviesIntoFile(commandLineArguments,moviesToInsertIntoFile)
        else:
            self.__outputMoviesToSTDOUT(moviesToInsertIntoFile)

        self.__logger.info('GoodMovies finished')

    def __initLogging(self,commandLineArguments):
        logging.basicConfig(filename=commandLineArguments.logfile,
                            filemode='a',
                            level=0,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __outputMoviesToSTDOUT(self,moviesToPrint):
        for eachMovieToPrint in moviesToPrint:
            print(eachMovieToPrint)

    def __insertMoviesIntoFile(self,
                               commandLineArguments,
                               moviesToInsertIntoFile):
        fileToWriteTo = io.open(commandLineArguments.outputfile,'a',encoding="utf8")

        for eachMovieToInsert in moviesToInsertIntoFile:
            fileToWriteTo.write(eachMovieToInsert)
            fileToWriteTo.write(u"\n")

        fileToWriteTo.close()

        self.__logger.info('Have added %i movies to file %s',
                           len(moviesToInsertIntoFile),
                           commandLineArguments.outputfile)

    def __findMoviesToInsertIntoFile(self,
                                     moviesAlreadyInFile,
                                     moviesThatShouldBeInFile):
        moviesToInsertIntoFile = []

        for eachMovieThatShouldBeInFile in moviesThatShouldBeInFile:
            if not eachMovieThatShouldBeInFile in moviesAlreadyInFile:
                self.__logger.info('Movie "%s" is not in file and will be added',eachMovieThatShouldBeInFile)
                moviesToInsertIntoFile.append(eachMovieThatShouldBeInFile)

        if len(moviesToInsertIntoFile) == 0:
            self.__logger.info('No new movies fetched, file will remain unchanged')

        return moviesToInsertIntoFile

    def __readMoviesThatShouldBeInFile(self,
                                       commandLineArguments):
        self.__logger.info('Fetching movies from list %s',commandLineArguments.list)

        theIMDBScraper = IMDBScraper()
        theIMDBScraper.setLanguage(commandLineArguments.language)

        if commandLineArguments.list == 'imdb_top250':
            moviesOnIMDBSite = theIMDBScraper.loadTop250()
        elif commandLineArguments.list.startswith('imdb_'):
            moviesOnIMDBSite = theIMDBScraper.loadTopMoviesByGenre(
                imdbGenreKey = commandLineArguments.list[5:],
                count = commandLineArguments.count)
        else:
            self.__logger.info('List "%s" is unknown, no movies fetched',commandLineArguments.list)
            moviesOnIMDBSite = []

        moviesThatShouldBeInFile = moviesOnIMDBSite[:commandLineArguments.count]

        self.__logger.info('Fetched %i movies, that should be in file',len(moviesThatShouldBeInFile))

        return moviesThatShouldBeInFile

    def __readMoviesAlreadyInFile(self,
                                  commandLineArguments):
        self.__logger.info('Reading file %s',commandLineArguments.outputfile)

        if commandLineArguments.outputfile != '':
            try:
                fileToUpdate = io.open(
                    commandLineArguments.outputfile,'r',encoding="utf8")

                contentInFileToUpdate = fileToUpdate.read()
                moviesAlreadyInFile = contentInFileToUpdate.rstrip().split("\n")
                fileToUpdate.close()
            except Exception as e:
                self.__logger.warning('Could not read file %s, maybe file does not exist yet',commandLineArguments.outputfile)
                moviesAlreadyInFile = []

            self.__logger.info('File %s already contains %i movies',commandLineArguments.outputfile,len(moviesAlreadyInFile))
        else:
            self.__logger.info('No outputfile specified - writing movies to STDOUT')
            moviesAlreadyInFile = []

        return moviesAlreadyInFile

    def __parseCommandLineArguments(self):
        parser = argparse.ArgumentParser(
            description='Fetch film lists from IMDB and write them to text files.')

        parser.add_argument(
            '-li','--list',
            help='the list to fetch, "imdb_top250" to fetch from the IMDB top 250 list, "imdb_<genre>" to fetch from the IMDB list with a special genre',
            choices=["imdb_top250",
                     "imdb_adventure",
                     "imdb_action",
                     "imdb_animation",
                     "imdb_biography",
                     "imdb_comedy",
                     "imdb_crime",
                     "imdb_drama",
                     "imdb_family",
                     "imdb_fantasy",
                     "imdb_film_noir",
                     "imdb_history",
                     "imdb_horror",
                     "imdb_music",
                     "imdb_musical",
                     "imdb_mystery",
                     "imdb_romance",
                     "imdb_sci_fi",
                     "imdb_sport",
                     "imdb_thriller",
                     "imdb_war",
                     "imdb_western" ],
            default="imdb_top250")

        parser.add_argument(
            '-la','--language',
            help='specify the language to retrieve the films in',
            default="en-US")

        parser.add_argument(
            '-of','--outputfile',
            help='specify the file the result should be written to',
            default='')

        parser.add_argument(
            '-lo','--logfile',
            help='specify the file the logging messages are appended to',
            default='/tmp/goodmovies.log')

        parser.add_argument(
            '-cn','--count',
            help='the number of films to write to the output file',
            type=int,
            default=100)

        return parser.parse_args()

def main():
    goodMoviesRunner = GoodMoviesRunner()
    goodMoviesRunner.execute()

if __name__ == "__main__":
    main()
