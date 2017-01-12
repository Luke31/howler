import json
from abc import abstractmethod, ABCMeta

from elasticsearch import helpers as es_helpers
from elasticsearch_dsl import Mapping, analysis, Text

from . import constants
from . import helpers
from ..dementor.mailextractor import MailExtractor


class Index(metaclass=ABCMeta):
    """Basic Index object:
    Mapping configuration for indices (email/irc)
    """

    def __init__(self, es_conn, es_index_prefix, es_type_name=constants.ES_TYPE_NAME_EMAIL,
                 user_dictionary_file=constants.JA_USER_DICT):
        """
        :param es_conn: Elasticsearch connection
        """
        self._es = es_conn  # Elasticsearch([constants.ES_HOST_IP], timeout=constants.ES_TIMEOUT, maxsize=25)
        self._index_prefix = es_index_prefix
        self._type_name = es_type_name
        self._user_dictionary_file = user_dictionary_file

    def add_mapping_to_index(self, lang_code, lang_analyzer, delete_old_index=False, kuromoji_synonyms=None):
        """
        :param lang_code: Language of index
        :param lang_analyzer: Name of analyzer for language
        :param delete_old_index: Delete index if existing? Default: False = Update existing index (Close, Update, Open)
        :param kuromoji_synonyms: Synonyms for kuromoji Japanese analyzer.
        Keep old synonyms if synonyms list empty and index not deleted
        :return: None
        """
        if kuromoji_synonyms is None:
            kuromoji_synonyms = []
        analyzer_lang = helpers.get_analyzer(lang_analyzer, delete_old_index=delete_old_index,
                                             user_dictionary_file=self._user_dictionary_file,
                                             synonyms=kuromoji_synonyms)
        analyzer_case_insensitive_sort = analysis.analyzer('case_insensitive_sort',
                                                           tokenizer=analysis.tokenizer('keyword'),
                                                           filter=['lowercase'])
        mapping = Mapping(self._type_name)
        reopen_index = False
        index_name = self._index_prefix.format(lang_code)
        if self._es.indices.exists(index=index_name):
            if delete_old_index:
                self._es.indices.delete(index=index_name, ignore=[400, 404])
            else:
                self._es.indices.close(index=index_name)
                reopen_index = True
                mapping = Mapping.from_es(index_name, self._type_name, using=self._es)  # Get existing index from server

        self.add_mapping_fields(mapping, analyzer_lang, analyzer_case_insensitive_sort)

        mapping.save(index_name, using=self._es)  # Insert or update

        if reopen_index:
            self._es.indices.open(index=index_name)

    @abstractmethod
    def add_mapping_fields(self, mapping, analyzer_lang, analyzer_case_insensitive_sort):
        pass


class IndexMail(Index):
    """Email Index object:
    Mapping configuration for emails of each supported language codes
    Index single file
    Index multiple files (iterator or dir)
    Index multiple files using bulk (iterator or dir)
    """

    def __init__(self, es_conn, es_index_prefix, es_type_name=constants.ES_TYPE_NAME_EMAIL,
                 user_dictionary_file=constants.JA_USER_DICT, mailextractor=MailExtractor()):
        """
        :param es_conn: Elasticsearch connection
        :param mailextractor: Parser for email-files to json (Default given)
        """
        super().__init__(es_conn, es_index_prefix, es_type_name=es_type_name, user_dictionary_file=user_dictionary_file)
        self._mailextractor = mailextractor
        self.already_imported_ids = helpers.get_already_imported_ids(es=self._es, es_index_prefix=self._index_prefix,
                                                                     es_type_name=self._type_name)
        self._cur_print = 0

    def add_mapping_to_index_multi(self, delete_old_indices=False, kuromoji_synonyms=None):
        if kuromoji_synonyms is None:
            kuromoji_synonyms = []
        for lang_code, lang_analyzer in constants.SUPPORTED_LANG_CODES_ANALYZERS.items():
            self.add_mapping_to_index(lang_code, lang_analyzer, delete_old_indices, kuromoji_synonyms)

    def add_mapping_fields(self, mapping, analyzer_lang, analyzer_case_insensitive_sort):
        # Specific fields email
        analyzer_email = analysis.analyzer('email', tokenizer=analysis.tokenizer('uax_url_email'),
                                           filter=['lowercase', 'unique'])
        mapping.field('fromName', 'text',
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('fromEmail', 'text', analyzer=analyzer_email,
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort, fielddata=True),
                      })
        mapping.field('toName', 'text',
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('toEmail', 'text', analyzer=analyzer_email,
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('replyToName', 'text',
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('replyToEmail', 'text', analyzer=analyzer_email,
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('subject', 'text', analyzer=analyzer_lang)
        mapping.field('date', 'date')
        mapping.field('body', 'text', analyzer=analyzer_lang)
        mapping.field('spam', 'boolean')
        mapping.field('hasAttachmet', 'boolean')
        mapping.field('attachmentNames', 'text')

    def index_bulk_from_dir(self, dir_data_in, ignore_already_imported=True):
        """
        Index all files from a directory using bulk-mode

        :param dir_data_in: ``str`` Path to dir in which all files should be indexed
        :param ignore_already_imported: ``bool`` Ignore mails which have already been imported to elasticsearch
        :return: Summary of completed bulk import
        """
        if ignore_already_imported:
            already_imported_ids = self.already_imported_ids
        else:
            already_imported_ids = set()
        return self.index_bulk_from_files(
            helpers.get_files_from_dir(dir_data_in, already_imported_ids=already_imported_ids))

    def index_bulk_from_files(self, files):
        """
        Index multiple mail-files into elasticsearch using Bulk-insert
        See: http://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers

        :param files: Any iterable, generator preferred for optimal memory usage
        :return: Summary of completed bulk import
        """

        docs = self._mailextractor.extract_jsons(files)  # Generator-Iterable
        actions = self.convert_docstrs_to_bulk_actions(docs)  # Generator-Iterable

        self._cur_print = 0
        actions_for_chunk = self.print_chunk_progress(actions)  # Generator-Iterable
        (cnt_success, errors_index) = es_helpers.bulk(
            self._es, actions_for_chunk, chunk_size=constants.ES_BULK_CHUNK_SIZE)

        cnt_total = self._mailextractor.cnt_total
        errors_convert = self._mailextractor.errors_convert
        cnt_error = len(errors_convert) + len(errors_index)
        return Summary(cnt_total=cnt_total, cnt_success=cnt_success, cnt_error=cnt_error,
                       errors_convert=errors_convert, errors_index=errors_index)

    def convert_docstrs_to_bulk_actions(self, docs):
        """
        Generator: Convert json doc-strings to bulk-import actions

        :param docs: List of tuples (Docid, email-JSON-str) Any iterable, generator preferred for optimal memory usage
        :return: actions (Generator-Iterable)
        """
        for (docid, docstr) in docs:
            data = json.loads(docstr)
            lang_code = get_lang_code(data['langCode'])

            data['_op_type'] = 'index'
            data['_index'] = self._index_prefix.format(lang_code)
            data['_type'] = self._type_name
            if docid.isdigit():
                data['_id'] = docid
            yield data

    def print_chunk_progress(self, actions):
        """
        Decorator for counting already converted emails.
        For every prepared chunk a message is print to console.

        :param actions: ``actions (Generator-Iterable`` actions to decorate
        :return: actions (Generator-Iterable)
        """
        for action in actions:
            if (self._cur_print % constants.ES_BULK_CHUNK_SIZE == 0) & (self._cur_print > 0):
                print("{0} emails converted. Starting bulk import (chunk size: {1})...".format(self._cur_print,
                                                                                               constants.ES_BULK_CHUNK_SIZE))
            self._cur_print += 1
            yield action


class IndexIrc(Index):
    """IRC Index object:
    Mapping configuration for IRC logs
    """

    def add_mapping_fields(self, mapping, analyzer_lang, analyzer_case_insensitive_sort):
        # Specific fields irc
        mapping.field('msg', 'text', analyzer=analyzer_lang,
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort)
                      })
        mapping.field('username', 'text',
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('@timestamp', 'date')

        mapping.field('channel', 'text',
                      fields={
                          'keyword': Text(analyzer=analyzer_case_insensitive_sort),
                      })
        mapping.field('tags', 'text',
                      fields={
                          'keyword': 'keyword',
                      })
        mapping.field('source', 'text',
                      fields={
                          'keyword': 'keyword',
                      })
        mapping.field('type', 'text',
                      fields={
                          'keyword': 'keyword',
                      })
        # mapping.field('message', 'text', analyzer=analyzer_lang)
        # mapping.field('geoip.ip', 'ip')
        # mapping.field('geoip.location', 'geo_point')
        # mapping.field('geoip.longitude', 'float')  # half_float
        # mapping.field('geoip.latitude', 'float')  # half_float
        #
        # mapping.field('beat.hostname', 'text',
        #               fields={
        #                   'keyword': 'keyword',
        #               })
        # mapping.field('beat.name', 'text',
        #               fields={
        #                   'keyword': 'keyword',
        #               })
        # mapping.field('beat.version', 'text',
        #               fields={
        #                   'keyword': 'keyword',
        #               })
        # mapping.field('host', 'text',
        #               fields={
        #                   'keyword': 'keyword',
        #               })
        mapping.field('@version', 'keyword')
        mapping.field('input_type', 'text',
                      fields={
                          'keyword': 'keyword',
                      })
        mapping.field('location', 'text',
                      fields={
                          'keyword': 'keyword',
                      })

        mapping.field('offset', 'long')


def get_lang_code(lang_code):
    """
    Check if provided lang_code is supported, if not, return fallback
    :param lang_code: ``str`` langauge code to check
    :return: ``str`` Supported language code
    """
    if lang_code not in constants.SUPPORTED_LANG_CODES_ANALYZERS:
        return constants.FALLBACK_LANG_CODE
    return lang_code


class Summary(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
