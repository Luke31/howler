from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Mapping, Text, Keyword, analysis
from ..dementor.mailextractor import MailExtractor
from . import constants
from . import helpers

import os
import json


class Index:
    """Basic Index object:
    Mapping configuration for emails of each supported language codes
    Index single file
    Index multiple files (iterator or dir)
    Index multiple files using bulk (iterator or dir)
    """

    def __init__(self, mailextractor=MailExtractor()):
        # self._es = Elasticsearch()
        self._es = Elasticsearch([constants.ES_HOST_IP], maxsize=25)
        self._mailextractor = mailextractor
        self._index_name = constants.ES_INDEX_PREFIX
        self._type_name = constants.ES_TYPE_NAME

    def add_mapping_to_index_multi(self):
        for lang_code, lang_analyzer in constants.SUPPORTED_LANG_CODES_ANALYZERS.items():
            self.add_mapping_to_index(lang_code, lang_analyzer)

    def add_mapping_to_index(self, lang_code, lang_analyzer):
        analyzer_lang = analysis.analyzer(lang_analyzer)
        analyzer_email = analysis.analyzer('email', tokenizer=analysis.tokenizer('uax_url_email'),
                                           filter=['lowercase', 'unique'])

        m = Mapping(self._type_name)
        m.field('fromName', 'text',
                fields={
                    'raw': 'keyword',
                })
        m.field('fromEmail', 'text', analyzer=analyzer_email)
        m.field('toName', 'text',
                fields={
                    'raw': 'keyword',
                })
        m.field('toEmail', 'text', analyzer=analyzer_email)
        m.field('replyToName', 'text',
                fields={
                    'raw': 'keyword',
                })
        m.field('replyToEmail', 'text', analyzer=analyzer_email)
        m.field('subject', 'text', analyzer=analyzer_lang)
        m.field('date', 'date')
        m.field('body', 'text', analyzer=analyzer_lang)

        m.save(self._index_name.format(lang_code), using=self._es)

    def index_bulk_from_dir(self, dir_data_in):
        """
        Index all files from a directory using bulk-mode

        :param dir_data_in: Path to dir in which all files should be indexed
        :return: Summary of completed bulk import
        """
        return self.index_bulk_from_files(helpers.get_files_from_dir(dir_data_in))

    def index_bulk_from_files(self, files):
        """
        Index multiple mail-files into elasticsearch using Bulk-insert
        See: http://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers

        :param files: Any iterable, generator preferred for optimal memory usage
        :return: Summary of completed bulk import
        """

        docs = self._mailextractor.extract_jsons(files)  # Generator-Iterable
        cnt_total = self._mailextractor.cnt_total
        errors_convert = self._mailextractor.errors_convert

        actions = self.convert_docstrs_to_bulk_actions(docs)  # Generator-Iterable
        (cnt_success, errors_index) = helpers.bulk(self._es, actions, stats_only=False)
        # es_summary = helpers.parallel_bulk(self._es, actions, stats_only=False)

        cnt_error = len(errors_convert) + len(errors_index)
        return Summary(cnt_total=cnt_total, cnt_success=cnt_success, cnt_error=cnt_error,
                       errors_convert=errors_convert, errors_index=errors_index)

    def convert_docstrs_to_bulk_actions(self, docs):
        """
        Generator: Convert json doc-strings to bulk-import actions

        :param docs: List of tuples (Docid, email-data in json-str) Any iterable, generator preferred for optimal memory usage
        :return: actions (Generator-Iterable)
        """
        for (docid, docstr) in docs:
            data = json.loads(docstr)
            lang_code = get_lang_code(data['langCode'])

            data['_index'] = self._index_name.format(lang_code)
            data['_type'] = self._type_name
            if docid.isdigit():
                data['_id'] = docid
            yield json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)

    def index_from_file(self, file):
        """
        Index a single mail from file

        :param file: Path to file to index
        :return: 0 if success, 1 if failure (will be printed on console)
        """
        try:
            jsonstr = self._mailextractor.extract_json(file)
            docid = os.path.basename(file)
            self.index(docid, jsonstr)
            return 0
        except (LookupError, AttributeError, ValueError, TypeError, FileNotFoundError) as e:
            ret = 'An exception of type {0} occured, when reading file {1}: {2}'.format(type(e).__name__, file, e)
            print(ret)
            return 1

    def index(self, docid, docstr):
        """
        Index a json to elasticsearch.

        :param docid: id of new document to index
        :param docstr: json docstr, must contain property 'langCode'
        :return: elasticsearch index result
        """
        data = json.loads(docstr)
        lang_code = get_lang_code(data['langCode'])
        res = self._es.index(index=self._index_name.format(lang_code), doc_type=self._type_name, id=docid, body=docstr)
        return res


def get_lang_code(lang_code):
    if lang_code not in constants.SUPPORTED_LANG_CODES_ANALYZERS:
        return constants.FALLBACK_LANG_CODE
    return lang_code


if __name__ == "__main__":
    index = Index()
    index.add_mapping_to_index_multi()
    summary = index.index_bulk_from_dir(os.getcwd())
    print("Successfully indexed {0}/{1} emails. Errors on json-convert: {2}, Errors in indexing: {3}".format(
        summary.cnt_success, summary.cnt_total, len(summary.errors_convert), len(summary.errors_index)))


class Summary(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
