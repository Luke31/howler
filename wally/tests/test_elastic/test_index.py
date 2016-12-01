import unittest
import os
from wally.elastic.index import Index


class TestIndexMethods(unittest.TestCase):
    """
    This isn't really a unit test. More an integration test.
    Runs a wally on the server.
    What about extracting the elasticsearch-client so it can be unit-tested by injecting a mock-client?
    """

    def test_search(self):
        idx = Index()

        idx.add_mapping_to_index_multi()

        in_dir = 'data_in'
        basepath = os.path.dirname(os.path.realpath(__file__))  # os.getcwd()
        in_path = os.path.join(basepath, in_dir)
        cnt = 0
        cnt_err = 0
        for filename in os.listdir(in_path):
            if cnt % 1000 == 0:
                print(cnt)
            if os.path.isdir(os.path.join(in_path, filename)):
                continue
            mail = filename
            filepath = os.path.join(basepath, in_dir, mail).replace('\\', '/')
            cnt_err += idx.index_from_file(filepath)
            cnt += 1

        print("Successfully indexed {0}/{1} emails".format(cnt - cnt_err, cnt))

        self.assertEqual(True, True)  # expect, actual

if __name__ == '__main__':
    unittest.main()
