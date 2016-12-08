
ES_TYPE_NAME = 'email'

# Unused, old, new: pass own es-instance
# ES_HOST_IP = '10.0.10.180'
# ES_INDEX_PREFIX = 'mailing-{0}'
# ES_TIMEOUT = 30

SUPPORTED_LANG_CODES_ANALYZERS = {'ja': 'kuromoji',
                                  'en': 'english',
                                  'un': 'standard'}
FALLBACK_LANG_CODE = 'un'
JA_USER_DICT = 'userdict_ja.txt'  # /etc/elasticsearch/userdict_ja.txt
