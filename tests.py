#!/usr/bin/python
'''Test cases for goodmovies.py'''
import unittest
import subprocess
import os
import io
import shutil

class TestProgram(unittest.TestCase):

    def setUp(self):
        self.__clearTestDataDirectory()

    def test_savesTop250InEnglischToFile(self):
        """tests, whether we can read movies from the imdb top 250 list"""

        self.__runGoodMovies(["--list=imdb_top250",
                              "--language=en-US",
                              "--outputfile=testdata/top250englisch.txt"])
        writtenLines = self.__readTestFile("testdata/top250englisch.txt")

        # if count is not specified, a default of 100 is used
        self.assertEqual(len(writtenLines),100)
        self.assertEqual(writtenLines.count("The Shawshank Redemption"),1)

    def test_savesTop100SciFiInEnglischToFile(self):
        """tests, whether we can read movies from the imdb sci_fi list"""

        self.__runGoodMovies(["--list=imdb_sci_fi",
                              "--language=en-US",
                              "--outputfile=testdata/top100scifienglisch.txt"])
        writtenLines = self.__readTestFile("testdata/top100scifienglisch.txt")

        # if count is not specified, a default of 100 is used
        self.assertEqual(len(writtenLines),100)
        self.assertEqual(writtenLines.count("Blade Runner"),1)

    def test_savesTop150ActionInGermanToFile(self):
        """tests, whether we can read movies from the imdb action movie list
           in german"""

        self.__runGoodMovies(["--list=imdb_action",
                              "--language=de-DE",
                              "--count=150",
                              "--outputfile=testdata/top100actiongerman.txt"])
        writtenLines = self.__readTestFile("testdata/top100actiongerman.txt")

        self.assertEqual(len(writtenLines),150)
        self.assertEqual(writtenLines.count("Stirb langsam"),1)

    def test_savesTop250InGermanToFile(self):
        """tests, whether we can read movies from the imdb top 250 list
           in german"""

        self.__runGoodMovies(["--list=imdb_top250",
                              "--language=de-DE",
                              "--outputfile=testdata/top250german.txt"])
        writtenLines = self.__readTestFile("testdata/top250german.txt")

        self.assertEqual(len(writtenLines),100)
        self.assertEqual(writtenLines.count("Die Verurteilten"),1)

    def test_canSpecifyCount(self):
        """tests, whether we can read movies from the imdb top 250 list
           specifying a count"""

        self.__runGoodMovies(["--list=imdb_top250",
                              "--count=10",
                              "--language=de-DE",
                              "--outputfile=testdata/top10german.txt"])
        writtenLines = self.__readTestFile("testdata/top10german.txt")

        self.assertEqual(len(writtenLines),10)
        self.assertEqual(writtenLines.count("Die Verurteilten"),1)
        self.assertEqual(writtenLines.count("Gladiator"),0)

    def test_doesNotAddMovieTwice(self):
        """tests, that a movie is not added twice to the output file"""

        for x in range(0, 2):
            self.__runGoodMovies(["--list=imdb_top250",
                                  "--count=10",
                                  "--language=en-US",
                                  "--outputfile=testdata/top10english.txt"])

        writtenLines = self.__readTestFile("testdata/top10english.txt")

        self.assertEqual(len(writtenLines),10)
        self.assertEqual(writtenLines.count("The Shawshank Redemption"),1)

    def test_canSpecifyLogFile(self):
        """tests, that logging messages are appended to the log file given
           in the command line argument --logfile"""

        for x in range(0, 2):
            self.__runGoodMovies(["--list=imdb_top250",
                                  "--count=10",
                                  "--language=en-US",
                                  "--outputfile=testdata/top10english.txt",
                                  "--logfile=testdata/goodmovies.log"])

        writtenLog = self.__readTestFile("testdata/goodmovies.log")

        self.assertIn("GoodMovies started",writtenLog[0])
        self.assertIn("GoodMovies finished",writtenLog[-1])

    def test_callingWithoutOutputFileWritesToSTDOUT(self):
        """tests, that output is written to STDOUT, if parameter
           --outputfile is not given"""

        consoleOutput = self.__runGoodMovies(["--list=imdb_top250",
                                              "--count=10",
                                              "--language=en-US"])

        self.assertEqual(len(consoleOutput),10)
        self.assertEqual(consoleOutput.count("The Shawshank Redemption"),1)

    # the path the tests will create their data files in
    __testDataDirectory = 'testdata/'

    def __clearTestDataDirectory(self):
        """clears the files in test data directory, thereby only leaving
           the .gitignore file"""

        for eachFileInTestDataDirectory in os.listdir(self.__testDataDirectory):
            if eachFileInTestDataDirectory == '.gitignore':
                # we better keep the .gitignore file in the testdata directory
                continue

            filePath = os.path.join(self.__testDataDirectory, eachFileInTestDataDirectory)
            try:
                if os.path.isfile(filePath):
                    os.unlink(filePath)
            except Exception as e:
                print(e)

    def __runGoodMovies(self, options):
        """executes the goodmovies.py script and returns the console output"""

        callParameters = ["python","goodmovies.py"]
        callParameters.extend(options)

        outputOfGoodMovies = subprocess.check_output(callParameters)

        return outputOfGoodMovies.rstrip().split('\n')

    def __readTestFile(self, fileName):
        """reads the contents of the given file and returns
           the lines as list"""

        writtenFile = io.open(fileName,"r",encoding="utf8")
        writtenFileContent = writtenFile.read()
        writtenLines = writtenFileContent.rstrip().split("\n")

        return writtenLines

if __name__ == '__main__':
    unittest.main()
