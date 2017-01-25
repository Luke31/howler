# ES-type for emails
ES_TYPE_NAME_EMAIL = 'email'

# Supported languages with the specific ES-analyzer
SUPPORTED_LANG_CODES_ANALYZERS = {'ja': 'kuromoji',
                                  'en': 'english',
                                  'un': 'standard',
                                  'error': 'standard'}

# Fallback language if no supported language found
FALLBACK_LANG_CODE = 'un'

# File to store userdict for kuromoji tokenizer
JA_USER_DICT = 'userdict_ja.txt'  # /etc/elasticsearch/userdict_ja.txt

# Userdict term type (custom-term) for kuromoji tokenizer
# (See https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-kuromoji-tokenizer.html)
JA_USER_DICT_TERM_TYPE = 'カスタム名詞'

# ES Bulk insert chunk size
ES_BULK_CHUNK_SIZE = 2000

# Wally IRC day score-metric to search order-fields mapping
IRC_DAY_ORDER_FIELD = {'perc': 'percentiles_score_channel[99]',
                       'sum': 'sum_score_channel',
                       'max': 'max_score_channel'}
