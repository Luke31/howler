import os
from elasticsearch_dsl import Mapping, analysis
from . import constants


def get_files_from_dir(dir_data_in):
    """
    Generator: Returns all files in a dir (without dirs)

    :param dir_data_in: Path of input dir
    :return: File-paths (Generator-Iterable) in input-dir
    """
    if not os.path.isdir(dir_data_in):
        raise ValueError("Input dir invalid")

    for filename in os.listdir(dir_data_in):
        if os.path.isdir(os.path.join(dir_data_in, filename)):
            continue
        yield os.path.join(dir_data_in, filename).replace('\\', '/')


def get_analyzer(lang_analyzer, synonyms=[]):
    if lang_analyzer == constants.SUPPORTED_LANG_CODES_ANALYZERS['ja']:
        analyzer_lang = analysis.analyzer('{0}_custom'.format(lang_analyzer),
                                          tokenizer=analysis.tokenizer('kuromoji_tokenizer_user_dict',
                                                                       type='kuromoji_tokenizer',
                                                                       user_dictionary=constants.JA_USER_DICT),
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
