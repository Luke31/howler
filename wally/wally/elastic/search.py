from elasticsearch_dsl import Search as DslSearch, A
from elasticsearch_dsl.query import Boosting, Match, MatchPhrase, Term, Range, Q, SF, Common, SimpleQueryString, DisMax
from ..dementor import constants as dementor_constants
from . import constants as elastic_constants
from abc import abstractmethod, ABCMeta
import dateutil.parser
import copy
from . import helpers


class Search(metaclass=ABCMeta):
    """Base Search object - use specific child-class instead
    Search in elasticsearch indices
    """

    def __init__(self, es_conn, es_index_prefix, es_type_name):
        self._es = es_conn
        self._index_prefix = es_index_prefix
        self._type_name = es_type_name

    # noinspection PyIncorrectDocstring
    def search(self, qterm, **kwargs):
        r"""Searches in the elasticsearch index for the mail

            :param qterm:
                Query-string
            :type qterm: ``str``
            :param \**kwargs:
                See below

            :Keyword Arguments:
                * *date_gte* (``datetime``) --
                  Filter, From: only emails greater than
                * *date_lte* (``datetime``) --
                  Filter, To: only emails less than
                * *date_sliding* (``str``) --
                  Filter sliding window, only emails of the past XX-hours/days/years... e.g. '-1d/d','-5y/y' --
                  See: https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math
                * *date_sliding_type* (``str``) --
                  Valid date-type: e.g. y M d
                * *use_sliding_value* (``bool``) --
                  True: Only respect date_sliding and date_sliding_type.
                  False: only respect fix date: date_gte and date_lte
                * *number_results* (``int``) --
                  Number of total results to return
                * *sort_field* (``str``) --
                  By which field should results be sorted e.g. date, _score, fromEmail.keyword
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)
            :return: ``DslSearch Response``

            """

        number_results = 10

        # Get arguments
        date_gte = None  # '2010-01-31T22:28:14+0300'  # from
        date_lte = 'now'  # ''2012-09-20T17:41:14+0900' # 'now'  # to
        date_sliding_value = ''
        date_sliding_type = ''
        use_sliding_value = True
        sort_field = '_score'
        sort_dir = '-'
        for key, value in kwargs.items():
            if key == 'date_gte':
                date_gte = ('{:' + dementor_constants.JSON_DATETIME_FORMAT + '}').format(value)
            if key == 'date_lte':
                date_lte = ('{:' + dementor_constants.JSON_DATETIME_FORMAT + '}').format(value)
            if key == 'use_sliding_value':
                use_sliding_value = value
            if key == 'date_sliding_value':
                date_sliding_value = value
            if key == 'date_sliding_type':
                date_sliding_type = value
            if key == 'number_results':
                number_results = value
            if key == 'sort_field':
                sort_field = value
            if key == 'sort_dir':
                sort_dir = value

        # Prepare query
        s = DslSearch(using=self._es, index=self._index_prefix.format('*'))

        # Filter date
        date_field_name = self.get_date_field_name()
        if use_sliding_value & (date_sliding_value != '') & (date_sliding_type != ''):
            s = s.query('bool', filter=[
                Range(**{date_field_name: {'gte': 'now-{0}{1}'.format(date_sliding_value, date_sliding_type)}})])
            # s = s.filter('range', date={'gte': 'now-{0}{1}'.format(date_sliding_value, date_sliding_type)})
        elif date_gte is not None:
            s = s.query('bool', filter=[
                Range(**{date_field_name: {'lte': date_lte, 'gte': date_gte}})])
            # s = s.filter('range', date={'lte': date_lte, 'gte': date_gte})

        # Add query-specific fields
        s = self.add_query_fields(s, qterm, **kwargs)

        s = s.sort(
            ''.join((sort_dir, sort_field)),
            '-_score',
        )

        # Number of results
        s = s[0:number_results]

        # Execute
        response = s.execute()
        response_altered = self.alter_response(response)
        return response_altered

    @abstractmethod
    def add_query_fields(self, s, qterm, **kwargs):
        pass

    @abstractmethod
    def alter_response(self, response):
        pass

    @abstractmethod
    def get_date_field_name(self):
        pass


class SearchMail(Search):
    """Email Search object.
    Search in elasticsearch indices
    """

    # noinspection PyIncorrectDocstring
    def add_query_fields(self, s, qterm, **kwargs):
        r"""Searches in the elasticsearch index for the mail

            :param s:
                DSL-Query to modify
            :type s: ``DslSearch`` Elasticsearch DSL query
            :param qterm:
                Query-string
            :type qterm: ``str``
            :param \**kwargs:
                See below

            :Keyword Arguments:
                * *date_gte* (``datetime``) --
                  Filter, From: only emails greater than
                * *date_lte* (``datetime``) --
                  Filter, To: only emails less than
                * *date_sliding* (``str``) --
                  Filter sliding window, only emails of the past XX-hours/days/years... e.g. '-1d/d','-5y/y' --
                  See: https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math
                * *date_sliding_type* (``str``) --
                  Valid date-type: e.g. y M d
                * *use_sliding_value* (``bool``) --
                  True: Only respect date_sliding and date_sliding_type.
                  False: only respect fix date: date_gte and date_lte
                * *include_spam* (``bool``) --
                  True: Include spam in search (Both)
                  False: Spam will be filtered and not respected in search
                * *only_attachment* (``bool``) --
                  True: Only find emails with attachments
                  False: emails with and without attachments (Both)
                * *number_results* (``int``) --
                  Number of total results to return
                * *sort_field* (``str``) --
                  By which field should results be sorted e.g. date, _score, fromEmail.keyword
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)
            :return: ``DslSearch`` Elasticsearch DSL query

            """
        # Query
        fields = ['body', 'fromEmail', 'toEmail', 'replyToEmail', 'fromName', 'toName', 'replyToName', 'subject',
                  'attachmentNames']
        if helpers.is_simple_query_string_query(qterm):
            body_query = SimpleQueryString(query=qterm, fields=fields, default_operator='AND', boost=5)
        else:
            body_query = DisMax(tie_breaker=0.7, boost=1, queries=[
                SimpleQueryString(query=qterm, fields=fields, default_operator='AND', boost=1),
                MatchPhrase(body={'query': qterm, 'boost': 1}),
            ])
        pos = DisMax(tie_breaker=0.7, boost=1, queries=[
            body_query,
            Common(body={'query': qterm, 'cutoff_frequency': 0.001}),
        ])

        # penalize if spam
        neg = Match(subject={'query': 'spam'})
        boosting = Boosting(positive=pos, negative=neg, negative_boost=0.2)
        s = s.query(boosting)

        # Get specific query arguments
        include_spam = False
        only_attachment = False
        mailq = ''
        for key, value in kwargs.items():
            if key == 'include_spam':
                include_spam = value
            if key == 'only_attachment':
                only_attachment = value
            if key == 'mailq':
                mailq = value

        # Filter mail
        if mailq != '':
            s = s.filter(Match(**{'fromEmail.keyword':mailq}) | \
                         Match(**{'toEmail.keyword': mailq}) | \
                         Match(**{'replyToEmail.keyword': mailq}))

        # Filter spam
        if not include_spam:
            s = s.filter(~Match(subject={'query': 'spam'}))
            s = s.filter(~Term(spam=1))  # TODO: Spam-flag currently not in use, but for use with different spam filter

        # Filter attachment
        if only_attachment:
            s = s.filter('term', hasAttachment=True)

        # Extra
        s = s.extra(indices_boost={
            self._index_prefix.format('ja'): 1.5,
            self._index_prefix.format('en'): 1,
            self._index_prefix.format('un'): 0.5
        })
        s = s.extra(_source={'excludes': ['body']})  # Don't return body, too large, use link

        # Highlight
        s = s.highlight_options(order='score')
        s = s.highlight('body', fragment_size=50)
        # s = s.highlight('body', number_of_fragments=0)
        s = s.highlight('subject')
        s = s.highlight('fromEmail')
        s = s.highlight('toEmail')
        s = s.highlight('replyToEmail')
        s = s.highlight('fromEmail.keyword')
        s = s.highlight('toEmail.keyword')
        s = s.highlight('replyToEmail.keyword')
        s = s.highlight('fromName')
        s = s.highlight('toName')
        s = s.highlight('replyToName')
        s = s.highlight('attachmentNames')

        return s

    def alter_response(self, response):
        # Add highlighted emails
        for hit in response:
            if hasattr(hit.meta, 'highlight'):
                self.add_highlight_emails(hit)
        return response

    def get_date_field_name(self):
        return 'date'

    @staticmethod
    def add_highlight_emails(hit):
        """
        Map highlighted fromEmail/toEmail/replyToEmail.keyword attribute to highlight.fromEmail/toEmail/replyToEmail.

        Hit is directly modified, no value is returned

        :param hit: Hit to search and modify
        :return: None (hit directly modified)
        """
        if hasattr(hit.meta, 'highlight'):
            if hasattr(hit.meta.highlight, 'fromEmail.keyword'):
                hit.meta.highlight.fromEmail = hit.meta.highlight['fromEmail.keyword']
            if hasattr(hit.meta.highlight, 'toEmail.keyword'):
                hit.meta.highlight.toEmail = hit.meta.highlight['toEmail.keyword']
            if hasattr(hit.meta.highlight, 'replyToEmail.keyword'):
                hit.meta.highlight.replyToEmail = hit.meta.highlight['replyToEmail.keyword']

class SearchIrc(Search):
    """IRC Search object.
    Search in elasticsearch indices for IRC
    """

    # noinspection PyIncorrectDocstring
    def add_query_fields(self, s, qterm, **kwargs):
        r"""Searches in the elasticsearch index for irc messages

            :param s: DSL-Query to modify
            :type s: ``DslSearch``
            :param qterm: Query-string to find
            :type qterm: ``str``
            :param \**kwargs:
                See below

            :Keyword Arguments:
                * *date_gte* (``datetime``) --
                  Filter, From: only emails greater than
                * *date_lte* (``datetime``) --
                  Filter, To: only emails less than
                * *date_sliding* (``str``) --
                  Filter sliding window, only emails of the past XX-hours/days/years... e.g. '-1d/d','-5y/y' --
                  See: https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math
                * *date_sliding_type* (``str``) --
                  Valid date-type: e.g. y M d
                * *use_sliding_value* (``bool``) --
                  True: Only respect date_sliding and date_sliding_type.
                  False: only respect fix date: date_gte and date_lte
                * *number_results* (``int``) --
                  Number of total results to return
                * *sort_field* (``str``) --
                  By which field should results be sorted e.g. date, _score, username
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)
            :return: ``DslSearch`` Elasticsearch DSL query

            """
        # Query
        s = s.query(self._get_query(qterm))

        # Get specific query arguments
        filter_channel = ''
        for key, value in kwargs.items():
            if key == 'filter_channel':
                filter_channel = value

        # Filter channel if provided
        if filter_channel != '':
            s = s.filter('term', **{'channel.keyword': filter_channel})

        # Highlight
        s = s.highlight_options(order='score')
        s = s.highlight('msg', number_of_fragments=0)
        s = s.highlight('username')
        s = s.highlight('channel')

        return s

    def alter_response(self, response):
        return response

    def get_date_field_name(self):
        return '@timestamp'

    def search_close(self, origin_timestamp, channel, qterm, number_results):
        """
        Find log entries close to origin timestamp, filter by channel, highlight qterm and return them sorted by date.

        :param origin_timestamp: origin timestamp to find logs around
        :param channel: Channel to be filtered
        :param qterm: Term to be highlighted
        :param number_results: how many results
        :return: List of sorted log entries (Elastic-search response)
        :rtype: ``list``
        """
        # Prepare query
        s = DslSearch(using=self._es, index=self._index_prefix.format('*'))

        # Function score
        main_query_boosting = 1e-15  # only used for highlighting, not for scoring -> give very low signifance
        pos = MatchPhrase(msg={'query': qterm, 'boost': main_query_boosting}) | \
              Match(**{'username': {'query': qterm, 'boost': main_query_boosting}}) | \
              Match(channel={'query': qterm, 'boost': main_query_boosting}) | \
              Match(msg={'query': qterm, 'boost': main_query_boosting})
        main_query = (pos | Q('match_all'))

        function_score_query = Q(
            'function_score',
            query=main_query,
            functions=[
                SF('exp', **{'@timestamp': {"origin": origin_timestamp, "scale": "1m", "decay": 0.999}})
            ]
        )

        s = s.query(function_score_query)

        # filter channel
        s = s.filter('term', **{'channel.keyword': channel})

        # Number of results
        s = s[0:number_results]

        # Highlight
        s = s.highlight_options(order='score')
        s = s.highlight('msg', number_of_fragments=0)
        s = s.highlight('username')
        s = s.highlight('channel')

        # Execute
        response = s.execute()

        # Sort results
        response_sorted = sorted(response, key=lambda hit: hit['@timestamp'])

        return response_sorted

    def search_day(self, qterm, score_metric='perc', **kwargs):
        """
        Searches in the elasticsearch index for irc messages, grouped by day and channel.

        Uses the elasticsearch aggregation function to build following aggregation levels of the documents:

        - A: filter (day/channel) -> B: group by day (day-bucket) -> C: group by channel (channel-bucket)

        ----

        The channel-buckets are sorted by their 99-percentile of their containing document-scores (This means that 1%
        of all the documents in the channel-bucket have a higher score than the 99-percentile of the channel-bucket.
        In comparsion to sum or avg, the 99-percentile has the advantage that higher document-scores/matching documents
        in the channel-bucket are valued higher. Many lower document scores will be valued less or even ignored.)
        For each day the highest perc-score of all channel-buckets on that day is remembered as ``max_score_day``.
        The day-buckets are then sorted by this highest perc-score ``max_score_day``.

        Important: This case describes the behaviour with a ``score_metric`` == 'perc'. If ``score_metric`` is changed,
        the behaviour is the same, except another metric is used.

        Definition: a document is one log-message

        :param score_metric: ``str`` Which metric to use for calculating channel-bucket score.
            This metric will also be used for sorting these buckets.

            - 'perc' 99-percentile of documents in channel-bucket. -> High-matching documents are valued higher
            - 'sum' sum of all document scores in channel-bucket -> All documents equal, many medium-matching documents
                may "eat-up" high-matching ones.
            - 'max' highest document score in channel-bucket as channel-bucket score -> Returns the day and channel with
                the highest matching log-message. Other messages on that day in that channel will be ignored.
        :param qterm: ``str`` Query-string to find
        :param \**kwargs:
                See below

            :Keyword Arguments:
                * *date_gte* (``datetime``) --
                  Filter, From: only emails greater than
                * *date_lte* (``datetime``) --
                  Filter, To: only emails less than
                * *date_sliding* (``str``) --
                  Filter sliding window, only emails of the past XX-hours/days/years... e.g. '-1d/d','-5y/y' --
                  See: https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math
                * *date_sliding_type* (``str``) --
                  Valid date-type: e.g. y M d
                * *use_sliding_value* (``bool``) --
                  True: Only respect date_sliding and date_sliding_type.
                  False: only respect fix date: date_gte and date_lte
                * *number_results* (``int``) --
                  Number of total results to return
                * *sort_field* (``str``) --
                  By which field should results be sorted e.g. date, _score, username
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)
        :return:
        """
        number_results = 50
        number_top_hits = 5

        # Get arguments
        date_gte = None  # '2010-01-31T22:28:14+0300'  # from
        date_lte = 'now'  # ''2012-09-20T17:41:14+0900' # 'now'  # to
        date_sliding_value = ''
        date_sliding_type = ''
        use_sliding_value = True
        sort_field = '_score'
        sort_dir = '-'
        for key, value in kwargs.items():
            if key == 'date_gte':
                date_gte = ('{:' + dementor_constants.JSON_DATETIME_FORMAT + '}').format(value)
            if key == 'date_lte':
                date_lte = ('{:' + dementor_constants.JSON_DATETIME_FORMAT + '}').format(value)
            if key == 'use_sliding_value':
                use_sliding_value = value
            if key == 'date_sliding_value':
                date_sliding_value = value
            if key == 'date_sliding_type':
                date_sliding_type = value
            if key == 'number_results':
                number_results = value
            if key == 'sort_field':
                sort_field = value
            if key == 'sort_dir':
                sort_dir = value

        # Get specific query arguments
        filter_channel = ''
        for key, value in kwargs.items():
            if key == 'filter_channel':
                filter_channel = value

        # Prepare query
        s = DslSearch(using=self._es, index=self._index_prefix.format('*'))
        s = s[0:0]  # don't return other results, only aggregation

        # Search-Query
        s = s.query(self._get_query(qterm))

        # Prepare score-metric and corresponding order-field for buckets and couments
        percentiles_percents = 99
        percentiles_percents_field = '99.0'
        percentiles_percents_field_order = elastic_constants.IRC_DAY_ORDER_FIELD['perc']
        score_order_field = elastic_constants.IRC_DAY_ORDER_FIELD[score_metric]

        # Prepare aggregate-query:
        # Aggregation levels: A (date/channel filtered) -> B (bucket days) -> C (bucket channel)

        # A date/channel filtered
        filters = []
        # Date
        if use_sliding_value & (date_sliding_value != '') & (date_sliding_type != ''):
            filters.append({'range': {
                '@timestamp': {'gte': 'now-{0}{1}'.format(date_sliding_value, date_sliding_type), 'lte': 'now'}}})
        elif date_gte is not None:
            filters.append({'range': {'@timestamp': {'gte': date_gte, 'lte': date_lte}}})

        # Channel
        if filter_channel != '':
            filters.append({'term': {'channel.keyword': filter_channel}})

        a_log_filtered = A('filter', Q('bool', must=filters))

        # B bucket days
        b_bucket_days = A('date_histogram', field='@timestamp', interval='day', format='yyyy-MM-dd',
                          min_doc_count=1, order={'max_score_day': 'desc'})

        # C bucket channels
        c_bucket_channels = A('terms', field='channel.keyword',
                              min_doc_count=1, order={score_order_field: 'desc'})
        c_bucket_channels = c_bucket_channels \
            .metric('max_date', 'max', field='@timestamp') \
            .metric('sum_score_channel', 'sum', script={'inline': '_score', 'lang': 'painless'}) \
            .metric('max_score_channel', 'max', script={'inline': '_score', 'lang': 'painless'}) \
            .metric('percentiles_score_channel', 'percentiles', percents=[percentiles_percents],
                    script={'inline': '_score', 'lang': 'painless'}) \
            .metric('top_msg_hits', 'top_hits', size=number_top_hits,
                    highlight={'fields': {'msg': {}, 'username': {}, 'channel': {}}},
                    sort=[{'_score': {'order': 'desc'}}],
                    **{'_source': {
                        'includes': ['channel', 'username', '@timestamp', 'msg']}})

        # Stack aggregations Main -> A -> B -> C (reversed order)
        b_bucket_days.bucket('logs_per_channel', c_bucket_channels)
        b_bucket_days.metric('max_score_day', 'max', field=score_order_field)  # Add metric
        a_log_filtered.bucket('logs_per_day', b_bucket_days)
        s.aggs.bucket('logs_filtered', a_log_filtered)

        # Execute query
        response = s.execute()

        # Flatten days-channels buckets (see: http://stackoverflow.com/a/952952/2003325)
        bucket_days = response.aggregations.logs_filtered.logs_per_day.buckets
        bucket_channel_flat = [item for sub in bucket_days for item in sub.logs_per_channel.buckets]

        # Sort flattened buckets (one bucket is a channel per day)
        if sort_field == 'channel.keyword':
            def sort_lambda(bucket_channel):
                return bucket_channel['key']
        elif sort_field == '_score' and score_metric == 'perc':
            def sort_lambda(bucket_channel):
                return bucket_channel.percentiles_score_channel.values[percentiles_percents_field]
        elif sort_field == '_score':  # '@timestamp' or 'sum_score_channel' or 'max_score_channel'
            def sort_lambda(bucket_channel):
                return bucket_channel[score_order_field].value
        elif sort_field == '@timestamp':
            def sort_lambda(bucket_channel):
                return bucket_channel['max_date'].value
        sort_dir = 'desc' if sort_dir == '-' else 'asc'

        bucket_channel_flat_sorted = sorted(bucket_channel_flat,
                                            key=sort_lambda,
                                            reverse=(sort_dir == 'desc'))

        # Limit result-size
        number_results_buckets = int(number_results / 3)
        bucket_channel_flat_sorted = bucket_channel_flat_sorted[0:number_results_buckets]

        # Get hits to display from flattened buckets
        hit_list = []
        for channel_bucket in bucket_channel_flat_sorted:
            for hit in channel_bucket.top_msg_hits.hits.hits:
                if score_order_field == percentiles_percents_field_order:
                    score = channel_bucket.percentiles_score_channel.values[percentiles_percents_field]
                else:
                    score = channel_bucket[score_order_field].value
                hit.meta = {'score': score, 'highlight': {}}
                hit_src = hit['_source']
                hit.sent = dateutil.parser.parse(hit_src['@timestamp'])
                hit.day_raw = '{:%Y-%m-%d}'.format(hit.sent)
                hit.timestamp_raw = hit_src['@timestamp']
                hit.username = hit_src.username
                hit.channel = hit_src.channel
                hit.msg = hit_src.msg
                if hasattr(hit, 'highlight'):
                    hit.meta.highlight = copy.deepcopy(hit.highlight)
                hit.meta.id = hit['_id']
            hit_list[len(hit_list):] = channel_bucket.top_msg_hits.hits.hits  # create hits list

        return hit_list

    @staticmethod
    def _get_query(qterm):
        """
        Return query for search-term (used in search and search_day)

        :param qterm: ``str`` string to build query for
        :return: ``Query`` Search-Query
        """
        if helpers.is_simple_query_string_query(qterm):
            msg_query = SimpleQueryString(query=qterm, fields=['msg', 'username', 'channel'], default_operator='AND',
                                          boost=5)
        else:
            msg_query = DisMax(tie_breaker=0.7, boost=1, queries=[
                SimpleQueryString(query=qterm, fields=['username', 'channel'], default_operator='AND', boost=1),
                MatchPhrase(msg={'query': qterm, 'boost': 1})
            ])
        pos = DisMax(tie_breaker=0.7, boost=1, queries=[
            msg_query,
            Common(msg={'query': qterm, 'cutoff_frequency': 0.001})
        ])

        return pos
