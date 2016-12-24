import unittest
import imdblists

class TestFilmList(unittest.TestCase):

    def test_loads_top_200(self):
        imdb_top_250_films = imdblists.IMDBAccess().load_top_250()
        self.assertEqual(len(imdb_top_250_films),250)
        self.assertEqual(imdb_top_250_films.count("Die Verurteilten"),1)

if __name__ == '__main__':
    unittest.main()
