import unittest
import os
from wally.elastic.index import Index


class TestIndexMethods(unittest.TestCase):
    """
    This isn't really a unit test. More an integration test.
    Runs a wally on the server.
    What about extracting the elasticsearch-client so it can be unit-tested by injecting a mock-client?
    """

    def test_index(self):
        self.assertEqual(True, True)  # expect, actual


if __name__ == '__main__':
    unittest.main()
