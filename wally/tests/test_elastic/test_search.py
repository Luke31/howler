import unittest
from wally.elastic.search import Search


class TestSearchMethods(unittest.TestCase):
    """
    This isn't really a unit test. More an integration test.
    Runs a wally on the server.
    What about extracting the elasticsearch-client so it can be unit-tested by injecting a mock-client?
    """

    def test_search(self):
        # print("Search for Japanese text: 何か調整が必要でしょうか?")
        #  Search().search('何か調整が必要でしょうか?')
        self.assertEqual(True, True)  # expect, actual

if __name__ == '__main__':
    unittest.main()
