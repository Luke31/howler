from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as DslSearch
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Boosting, Match, MultiMatch, MatchPhrase
from ..dementor import constants as dementor_constants
from . import constants

class Search:
    """Basic Search object.


    """

    def __init__(self):
        self._es = Elasticsearch([constants.ES_HOST_IP], maxsize=25)

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

            """
        date_gte = None  # '2010-01-31T22:28:14+0300'  # from
        date_lte = 'now'  #  ''2012-09-20T17:41:14+0900' # 'now'  # to
        date_sliding = None
        for key, value in kwargs.items():
            if key == 'date_gte':
                date_gte = ('{:'+dementor_constants.JSON_DATETIME_FORMAT+'}').format(value)
            if key == 'date_lte':
                date_lte = ('{:'+dementor_constants.JSON_DATETIME_FORMAT+'}').format(value)
            if key == 'date_sliding':
                date_sliding = value

        s = DslSearch(using=self._es, index=constants.ES_INDEX_PREFIX.format('*'))

        # Query
        pos = MatchPhrase(body={'query': qterm, 'boost': 2}) | \
              Match(subject={'query': qterm, 'boost': 1.5}) | \
              Match(body=qterm)

        # pos = MultiMatch(query=qterm, type='phrase', boost=2.0, fields=['body']) \
        #      | MultiMatch(query=qterm, type='most_fields', fields=['body'])

        # penalize if spam
        neg = Match(subject={'query': 'spam'})

        boosting = Boosting(positive=pos, negative=neg, negative_boost=0.2)

        s = s.query(boosting)

        # Filter
        if date_gte is not None:
            s = s.filter('range', date={'lte': date_lte, 'gte': date_gte})
        elif date_sliding is not None:
            s = s.filter('range', date={'gte': 'now-{0}'.format(date_sliding)})

        # Extra
        s = s.extra(indices_boost={
            constants.ES_INDEX_PREFIX.format('ja'): 1,
            constants.ES_INDEX_PREFIX.format('en'): 1,
            constants.ES_INDEX_PREFIX.format('un'): 0.5
        })

        # Highlight
        s = s.highlight_options(order='score')
        s = s.highlight('body', fragment_size=50)
        # s = s.highlight('body', number_of_fragments=0)
        s = s.highlight('subject')

        # Execute
        response = s.execute()

        # Multiple languages: https://www.elastic.co/guide/en/elasticsearch/guide/current/mixed-lang-fields.html
        # Identifying languages: https://www.elastic.co/guide/en/elasticsearch/guide/current/language-pitfalls.html#identifying-language

        return response

    def search_low(self, qterm):
        response = self._es.search(
            index="test-email-results.html",
            body=
            {
                "query": {
                    "boosting": {
                        "positive": [{
                            "bool": {
                                "should": [
                                    {
                                        "multi_match": {
                                            "query": qterm,
                                            "type": "phrase",
                                            "fields": ["body"],
                                            "boost": 2.0
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "query": qterm,
                                            "type": "most_fields",
                                            "fields": ["body"]
                                        }
                                    }
                                ]
                            }
                        }],
                        "negative": [
                            {
                                "bool": {
                                    "should": [
                                        {
                                            "match": {
                                                "subject": "spam"
                                            }
                                        }
                                    ]
                                }
                            }
                        ],
                        "negative_boost": 0.2
                    }
                }
            }
        )

        for hit in response['hits']['hits']:
            print(hit['_score'], '\n', hit['subject'])
            for fragment in hit.meta.highlight.body:
                print(fragment)

        for hit in response:
            if hasattr(hit, 'buildNum'):
                continue
            print(hit.meta.score, '\n', hit.subject)
            if hasattr(hit, '_highlight.body'):
                for fragment in hit['_highlight.body']:
                    print(fragment)

            if hasattr(hit, '_highlight.subject'):
                for fragment in hit['_highlight.subject']:
                    print(fragment)
        return response
