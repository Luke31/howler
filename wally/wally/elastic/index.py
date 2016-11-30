from elasticsearch import Elasticsearch
from elasticsearch_dsl import Mapping, Text, Keyword, analysis
from ..dementor.mailextractor import MailExtractor
from . import constants

import os
import json


class Index:
    """Basic Search object.

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
        analyzer_email = analysis.analyzer('email', tokenizer=analysis.tokenizer('uax_url_email'), filter=['lowercase', 'unique'])

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
        m.field('subject','text', analyzer=analyzer_lang)
        m.field('date', 'date')
        m.field('body', 'text', analyzer=analyzer_lang)

        m.save(self._index_name.format(lang_code), using=self._es)

    def index_from_file(self, file):
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
        data = json.loads(docstr)
        lang_code = data['langCode']
        if lang_code not in constants.SUPPORTED_LANG_CODES_ANALYZERS:
            lang_code = constants.FALLBACK_LANG_CODE
        res = self._es.index(index=self._index_name.format(lang_code), doc_type=self._type_name, id=docid, body=docstr)
