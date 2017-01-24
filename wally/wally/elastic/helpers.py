import os
from elasticsearch_dsl import Mapping, analysis
from . import constants
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import re


def get_already_imported_ids(es, es_index_prefix, es_type_name):
    """
    Returns existing EL-ids of provided index and type.

    :param es: es-connection instance
    :param es_index_prefix: ``str`` Index prefix
    :param es_type_name: ``str`` ES document type name
    :return: ``set`` Set of already imported ids (Read time if id exists: O(1))
    """
    index_name = es_index_prefix.format('*')
    s = Search(using=es, index=index_name, doc_type=es_type_name)
    s = s.extra(stored_fields=[])
    ids = set()
    for h in s.scan():
        ids.add(h.meta.id)
    return ids


def get_files_from_dir(dir_data_in, already_imported_ids):
    """
    Generator: Return all files in a dir (without dirs)

    :param dir_data_in: ``str`` Path of input dir
    :param already_imported_ids: ``set`` Ignore file if already in imported set
    :return: ``str`` File-paths (Generator-Iterable) in input-dir
    """
    if not os.path.isdir(dir_data_in):
        raise ValueError("Input dir invalid")

    for filename in os.listdir(dir_data_in):
        if os.path.isdir(os.path.join(dir_data_in, filename)):
            continue
        try:
            int(filename)
        except ValueError:
            continue  # only accept int-files (will be used as id)
        # ignore if no number
        # ignore if already imported
        if filename in already_imported_ids:
            continue
        yield os.path.join(dir_data_in, filename).replace('\\', '/')


def get_analyzer(lang_analyzer, delete_old_index, user_dictionary_file='', synonyms=None):
    """
    Return analyzer for specific language.

    If Japanese (``lang_analyzer == ja``) and the index doesn't need to be recreated (no delete required and
    no new synonyms) then return only the name of the analyzer.

    :param lang_analyzer: ``str`` which analyzer to get e.g. 'standard','kuromoji','english'
    :param delete_old_index: (only Japanese) ``bool`` if list is empty and index is not deleted, keep previous analyzer
        with synonyms
    :param user_dictionary_file: (only Japanese) ``str`` user-dictionary file with custom terms in the form of
        東京スカイツリー,東京 スカイツリー,トウキョウ スカイツリー,カスタム名詞
        See: https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-kuromoji-tokenizer.html
    :param synonyms: (only Japanese) ``list`` of synonyms to be used in the form of ['京産大, 京都産業大学','a, b']
        if list is empty and index is not deleted, keep previous analyzer with synonyms
    :return: ``analyzer`` or ``str`` of analyzer to be used
    """
    if synonyms is None:
        synonyms = []
    if lang_analyzer == constants.SUPPORTED_LANG_CODES_ANALYZERS['ja']:
        # Use existing analyzer (with synonyms) if new synonyms list is empty. (Only if index is not re-built)
        if (not delete_old_index) & (len(synonyms) == 0):
            analyzer_lang = '{0}_custom'.format(lang_analyzer)  # Use existing analyzer with existing synonyms
        else:
            analyzer_lang = analysis.analyzer('{0}_custom'.format(lang_analyzer),
                                              tokenizer=analysis.tokenizer('kuromoji_tokenizer_user_dict',
                                                                           type='kuromoji_tokenizer',
                                                                           user_dictionary=user_dictionary_file),
                                              filter=['kuromoji_baseform', 'kuromoji_part_of_speech', 'cjk_width',
                                                      'ja_stop', 'kuromoji_stemmer', 'lowercase',
                                                      analysis.token_filter('synonym', type='synonym',
                                                                            synonyms=synonyms),  # ['京産大, 京都産業大学']
                                                      ])
            # Extra token filters: kuromoji_number, kuromoji_readingform
            # Extra character filter: kuromoji_iteration_mark
            # user_dictionary="userdict_ja.txt")  # /etc/elasticsearch/
    else:
        analyzer_lang = analysis.analyzer(lang_analyzer)
    return analyzer_lang


def is_simple_query_string_query(qterm):
    """
    Returns true if the qterm contains elasticsearch simple query string query syntax.

    :param qterm: Query string to analyze
    :return: ``bool``
    """
    return bool(re.search('^.*[-+|"*()~].*$', qterm))
