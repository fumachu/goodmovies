import unittest
import subprocess
import os
import io
import shutil

class TestProgram(unittest.TestCase):

    def setUp(self):
        self.__clearTestDataDirectory()

    def test_savesTop250InEnglischToFile(self):
        self.__runGoodMovies(["--list=top250",
                              "--language=en-US",
                              "--outputfile=testdata/top250englisch.txt"])
        writtenLines = self.__readTestFile("testdata/top250englisch.txt")

        # if count is not specified, a default of 100 is used
        self.assertEqual(len(writtenLines),100)
        self.assertEqual(writtenLines.count("The Shawshank Redemption"),1)

    def test_savesTop250InGermanToFile(self):
        self.__runGoodMovies(["--list=top250",
                              "--language=de-DE",
                              "--outputfile=testdata/top250german.txt"])
        writtenLines = self.__readTestFile("testdata/top250german.txt")

        self.assertEqual(len(writtenLines),100)
        self.assertEqual(writtenLines.count("Die Verurteilten"),1)

    def test_canSpecifyCount(self):
        self.__runGoodMovies(["--list=top250",
                              "--count=10",
                              "--language=de-DE",
                              "--outputfile=testdata/top10german.txt"])
        writtenLines = self.__readTestFile("testdata/top10german.txt")

        self.assertEqual(len(writtenLines),10)
        self.assertEqual(writtenLines.count("Die Verurteilten"),1)
        self.assertEqual(writtenLines.count("Gladiator"),0)

    def test_doesNotAddFilmTwice(self):
        for x in range(0, 2):
            self.__runGoodMovies(["--list=top250",
                                  "--count=10",
                                  "--language=en-US",
                                  "--outputfile=testdata/top10english.txt"])

        writtenLines = self.__readTestFile("testdata/top10english.txt")

        self.assertEqual(len(writtenLines),10)
        self.assertEqual(writtenLines.count("The Shawshank Redemption"),1)

    # the path the tests will create their data files in
    __testDataDirectory = 'testdata/'

    def __clearTestDataDirectory(self):
        for eachFileInTestDataDirectory in os.listdir(self.__testDataDirectory):
            filePath = os.path.join(self.__testDataDirectory, eachFileInTestDataDirectory)
            try:
                if os.path.isfile(filePath):
                    os.unlink(filePath)
            except Exception as e:
                print(e)

    def __runGoodMovies(self,options):
        callParameters = ["python","goodmovies.py"]
        callParameters.extend(options)
        subprocess.check_call(callParameters)

    def __readTestFile(self,fileName):
        writtenFile = io.open(fileName,"r",encoding="utf8")
        writtenFileContent = writtenFile.read()
        writtenLines = writtenFileContent.rstrip().split("\n")

        return writtenLines

if __name__ == '__main__':
    unittest.main()
