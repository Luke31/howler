import os
from elasticsearch_dsl import Mapping, analysis
from . import constants
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def get_already_imported_ids(es, es_index_prefix, es_type_name):
    """
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
    Generator: Returns all files in a dir (without dirs)

    :param dir_data_in: ``str`` Path of input dir
    :param already_imported_ids: ``set`` Ignore file if already in imported set
    :return: ``str`` File-paths (Generator-Iterable) in input-dir
    """
    if not os.path.isdir(dir_data_in):
        raise ValueError("Input dir invalid")

    for filename in os.listdir(dir_data_in):
        if os.path.isdir(os.path.join(dir_data_in, filename)):
            continue
        # ignore if already imported
        if filename in already_imported_ids:
            continue
        yield os.path.join(dir_data_in, filename).replace('\\', '/')


def get_analyzer(lang_analyzer, delete_old_index, user_dictionary_file='', synonyms=[]):
    if lang_analyzer == constants.SUPPORTED_LANG_CODES_ANALYZERS['ja']:
        # Use existing analyzer (with synonyms) if new synonyms list is empty. (Only if index is not re-built)
        if ~delete_old_index & len(synonyms) == 0:
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
