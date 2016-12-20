import unittest
import os
from elasticsearch_dsl import Mapping, analysis
import wally.elastic.helpers as helpers


class TestIndexMethods(unittest.TestCase):
    """
    Testing helper methods
    """

    def test_get_analyzer_standard(self):
        analyzer_lang = helpers.get_analyzer(lang_analyzer='standard', delete_old_index=False)
        self.assertIsInstance(analyzer_lang, analysis.BuiltinAnalyzer)
        self.assertEqual(analyzer_lang._name, 'standard')

    def test_get_analyzer_english(self):
        analyzer_lang = helpers.get_analyzer(lang_analyzer='english', delete_old_index=False)
        self.assertIsInstance(analyzer_lang, analysis.BuiltinAnalyzer)
        self.assertEqual(analyzer_lang._name, 'english')

    def test_get_analyzer_english(self):
        analyzer_lang = helpers.get_analyzer(lang_analyzer='inexistentanalyzer', delete_old_index=False)
        self.assertIsInstance(analyzer_lang, analysis.BuiltinAnalyzer)
        self.assertEqual(analyzer_lang._name, 'inexistentanalyzer')

    def test_get_analyzer_kuromoji_keep_old(self):
        analyzer_lang = helpers.get_analyzer(lang_analyzer='kuromoji', delete_old_index=False)
        self.assertEqual(analyzer_lang, 'kuromoji_custom')

    def test_get_analyzer_kuromoji_new_synonyms_so_create_new(self):
        analyzer_lang = helpers.get_analyzer(lang_analyzer='kuromoji', delete_old_index=False, synonyms=['a, b'])
        self.assertIsInstance(analyzer_lang, analysis.CustomAnalyzer)
        self.assertEqual(analyzer_lang._name, 'kuromoji_custom')

        custom_filter_list = list(f for f in analyzer_lang._params['filter'] if isinstance(f, analysis.CustomTokenFilter))
        self.assertEqual(len(custom_filter_list), 1)
        custom_filter = custom_filter_list[0]
        self.assertEqual(custom_filter._name, 'synonym')
        self.assertEqual(custom_filter._params['synonyms'], ['a, b'])


if __name__ == '__main__':
    unittest.main()
