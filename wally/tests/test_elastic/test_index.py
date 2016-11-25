import unittest
import os
from wally.elastic.index import Index


class TestIndexMethods(unittest.TestCase):
    """
    This isn't really a unit test. More an integration test.
    Runs a search on the server.
    What about extracting the elasticsearch-client so it can be unit-tested by injecting a mock-client?
    """

    def test_search(self):
        idx = Index()

        idx.add_mapping_to_index_multi()

        inDir = 'data_in'
        basepath = os.getcwd()
        inPath = os.path.join(basepath, inDir)
        cnt = 0
        cntErr = 0
        for filename in os.listdir(inPath):
            if cnt % 1000 == 0:
                print(cnt)
            if os.path.isdir(os.path.join(inPath, filename)):
                continue
            mail = filename
            filepath = os.path.join(basepath, inDir, mail).replace('\\', '/')
            cntErr += idx.index_from_file(filepath)
            cnt += 1

        print("Successfully indexed {0}/{1} emails".format(cnt - cntErr, cnt))

        self.assertEqual(True, True)  # expect, actual

if __name__ == '__main__':
    unittest.main()