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

    def __fetchIMDBSiteContent(self,url):
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

        self.__insertMoviesIntoFile(commandLineArguments,moviesToInsertIntoFile)

        self.__logger.info('GoodMovies finished')

    def __initLogging(self,commandLineArguments):
        logging.basicConfig(filename=commandLineArguments.logfile,
                            filemode='a',
                            level=0,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        moviesOnIMDBSite = theIMDBScraper.loadTop250()
        moviesThatShouldBeInFile = moviesOnIMDBSite[:commandLineArguments.count]

        self.__logger.info('Fetched %i movies, that should be in file',len(moviesThatShouldBeInFile))

        return moviesThatShouldBeInFile

    def __readMoviesAlreadyInFile(self,
                                  commandLineArguments):

        self.__logger.info('Reading file %s',commandLineArguments.outputfile)

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

        return moviesAlreadyInFile

    def __parseCommandLineArguments(self):
        parser = argparse.ArgumentParser(
            description='Fetch film lists from IMDB and write them to text files.')

        parser.add_argument(
            '-li','--list',
            help='the list to fetch, now only top250 is supported')

        parser.add_argument(
            '-la','--language',
            help='specify the language to retrieve the films in',
            default="en-US")

        parser.add_argument(
            '-of','--outputfile',
            help='specify the file the result should be written to')

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
