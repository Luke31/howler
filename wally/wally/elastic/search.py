from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as DslSearch
from elasticsearch_dsl.query import Boosting, Match, MatchPhrase, Term
from ..dementor import constants as dementor_constants
from . import constants


class Search:
    """Base Search object - use specific child-class instead
    Search in elasticsearch indices
    """

    def __init__(self, es_conn, es_index_prefix, es_type_name):
        self._es = es_conn  # Elasticsearch([constants.ES_HOST_IP], timeout=constants.ES_TIMEOUT, maxsize=25)
        self._index_prefix = es_index_prefix
        self._type_name = es_type_name

    # noinspection PyIncorrectDocstring
    def _search(self, qterm, **kwargs):
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
                  By which field should results be sorted e.g. date, _score, fromEmail.raw
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)

            """

        number_results = 10

        sort_field = '_score'
        sort_dir = '-'
        for key, value in kwargs.items():
            if key == 'number_results':
                number_results = value
            if key == 'sort_field':
                sort_field = value
            if key == 'sort_dir':
                sort_dir = value

        s = DslSearch(using=self._es, index=self._index_prefix.format('*'))

        s = s.sort(
            ''.join((sort_dir, sort_field)),
            '-_score',
        )

        # Number of results
        s = s[0:number_results]

        return s

    @staticmethod
    def get_date_kwargs(**kwargs):
        date_gte = None  # '2010-01-31T22:28:14+0300'  # from
        date_lte = 'now'  # ''2012-09-20T17:41:14+0900' # 'now'  # to
        date_sliding_value = ''
        date_sliding_type = ''
        use_sliding_value = True
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
        return date_gte, date_lte, use_sliding_value, date_sliding_value, date_sliding_type


class SearchMail(Search):
    """Email Search object.
    Search in elasticsearch indices
    """

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
                * *include_spam* (``bool``) --
                  True: Include spam in search (Both)
                  False: Spam will be filtered and not respected in search
                * *only_attachment* (``bool``) --
                  True: Only find emails with attachments
                  False: emails with and without attachments (Both)
                * *number_results* (``int``) --
                  Number of total results to return
                * *sort_field* (``str``) --
                  By which field should results be sorted e.g. date, _score, fromEmail.raw
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)

            """
        s = super(SearchMail, self)._search(qterm, **kwargs)

        # Query
        pos = MatchPhrase(body={'query': qterm, 'boost': 2}) | \
              Match(fromEmail={'query': qterm, 'boost': 2}) | \
              Match(toEmail={'query': qterm, 'boost': 2}) | \
              Match(replyToEmail={'query': qterm, 'boost': 2}) | \
              Match(fromName={'query': qterm, 'boost': 1}) | \
              Match(toName={'query': qterm, 'boost': 1}) | \
              Match(replyToName={'query': qterm, 'boost': 1}) | \
              Match(subject={'query': qterm, 'boost': 1.5}) | \
              Match(attachmentNames={'query': qterm, 'boost': 2}) | \
              Match(body=qterm)

        # penalize if spam
        neg = Match(subject={'query': 'spam'})

        boosting = Boosting(positive=pos, negative=neg, negative_boost=0.2)

        s = s.query(boosting)

        include_spam = False
        only_attachment = False
        for key, value in kwargs.items():
            if key == 'include_spam':
                include_spam = value
            if key == 'only_attachment':
                only_attachment = value

        # Filter Date
        date_gte, date_lte, use_sliding_value, date_sliding_value, date_sliding_type = super(
            SearchMail, self).get_date_kwargs(**kwargs)
        if use_sliding_value & (date_sliding_value != '') & (date_sliding_type != ''):
            s = s.filter('range', date={'gte': 'now-{0}{1}'.format(date_sliding_value, date_sliding_type)})
        elif date_gte is not None:
            s = s.filter('range', date={'lte': date_lte, 'gte': date_gte})

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
        s = s.highlight('fromName')
        s = s.highlight('toName')
        s = s.highlight('replyToName')
        s = s.highlight('attachmentNames')

        # Execute
        response = s.execute()

        # Multiple languages: https://www.elastic.co/guide/en/elasticsearch/guide/current/mixed-lang-fields.html

        # Identifying languages:
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/language-pitfalls.html#identifying-language

        return response


class SearchIrc(Search):
    """IRC Search object.
    Search in elasticsearch indices for IRC
    """

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
                  By which field should results be sorted e.g. date, _score, fromEmail.raw
                * *sort_dir* (``str``) --
                  In Which direction should results be sorted
                  '+': ascending
                  '-': descending)

            """
        s = super(SearchIrc, self)._search(qterm, **kwargs)

        # Query
        pos = MatchPhrase(msg={'query': qterm, 'boost': 2}) | \
              Match(username={'query': qterm, 'boost': 2}) | \
              Match(channel={'query': qterm, 'boost': 2}) | \
              Match(msg=qterm)
        # neg = Match(subject={'query': 'spam'})
        # boosting = Boosting(positive=pos, negative=neg, negative_boost=0.2)

        s = s.query(pos)

        # Filter Date
        date_gte, date_lte, use_sliding_value, date_sliding_value, date_sliding_type = super(
            SearchMail, self).get_date_kwargs(**kwargs)
        if use_sliding_value & (date_sliding_value != '') & (date_sliding_type != ''):
            s = s.filter('range', date={'gte': 'now-{0}{1}'.format(date_sliding_value, date_sliding_type)})
        elif date_gte is not None:
            s = s.filter('range', date={'lte': date_lte, 'gte': date_gte})

        # Highlight
        s = s.highlight_options(order='score')
        s = s.highlight('msg', number_of_fragments=0)
        s = s.highlight('username')
        s = s.highlight('channel')

        # Execute
        response = s.execute()

        return response
