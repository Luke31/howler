ES_TYPE_NAME_EMAIL = 'email'

SUPPORTED_LANG_CODES_ANALYZERS = {'ja': 'kuromoji',
                                  'en': 'english',
                                  'un': 'standard',
                                  'error': 'standard'}
FALLBACK_LANG_CODE = 'un'
JA_USER_DICT = 'userdict_ja.txt'  # /etc/elasticsearch/userdict_ja.txt
JA_USER_DICT_TERM_TYPE = 'カスタム名詞'
ES_BULK_CHUNK_SIZE = 2000

