import argparse
import io
import urllib2
from bs4 import BeautifulSoup, SoupStrainer

class IMDBScraper:
    __language = "en-US"

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
    def execute(self):
        commandLineArguments = self.__parseCommandLineArguments()

        moviesThatShouldBeInFile = self.__readMoviesThatShouldBeInFile(commandLineArguments)
        moviesAlreadyInFile = self.__readMoviesAlreadyInFile(commandLineArguments)
        moviesToInsertIntoFile = self.__findMoviesToInsertIntoFile(moviesAlreadyInFile,moviesThatShouldBeInFile)

        self.__insertMoviesIntoFile(commandLineArguments,moviesToInsertIntoFile)

    def __insertMoviesIntoFile(self,
                               commandLineArguments,
                               moviesToInsertIntoFile):
        fileToWriteTo = io.open(commandLineArguments.outputfile,'a',encoding="utf8")

        for eachMovieToInsert in moviesToInsertIntoFile:
            fileToWriteTo.write(eachMovieToInsert)
            fileToWriteTo.write(u"\n")

        fileToWriteTo.close()

    def __findMoviesToInsertIntoFile(self,
                                     moviesAlreadyInFile,
                                     moviesThatShouldBeInFile):
        moviesToInsertIntoFile = []

        for eachMovieThatShouldBeInFile in moviesThatShouldBeInFile:
            if not eachMovieThatShouldBeInFile in moviesAlreadyInFile:
                moviesToInsertIntoFile.append(eachMovieThatShouldBeInFile)

        return moviesToInsertIntoFile

    def __readMoviesThatShouldBeInFile(self,
                                       commandLineArguments):
        theIMDBScraper = IMDBScraper()
        theIMDBScraper.setLanguage(commandLineArguments.language)
        moviesOnIMDBSite = theIMDBScraper.loadTop250()
        moviesThatShouldBeInFile = moviesOnIMDBSite[:commandLineArguments.count]

        return moviesThatShouldBeInFile

    def __readMoviesAlreadyInFile(self,
                                  commandLineArguments):
        try:
            fileToUpdate = io.open(
                commandLineArguments.outputfile,'r',encoding="utf8")

            contentInFileToUpdate = fileToUpdate.read()
            moviesAlreadyInFile = contentInFileToUpdate.rstrip().split("\n")
            fileToUpdate.close()
        except Exception as e:
            moviesAlreadyInFile = []

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
