from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as DslSearch
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Boosting, Match, MultiMatch, MatchPhrase
from . import constants


class Search:
    """Basic Search object.


    """

    def __init__(self):
        self._es = Elasticsearch([constants.ES_HOST_IP], maxsize=25)

    def search(self, qterm):
        pos = MatchPhrase(body={'query':qterm, 'boost':2}) | \
              Match(subject={'query': qterm, 'boost':1.5}) | \
              Match(body=qterm)

        #pos = MultiMatch(query=qterm, type='phrase', boost=2.0, fields=['body']) \
        #      | MultiMatch(query=qterm, type='most_fields', fields=['body'])

        neg = Match(subject={'query': 'spam'})

        boosting = Boosting(positive=pos, negative=neg, negative_boost=0.2)

        s = DslSearch(using=self._es, index=constants.ES_INDEX_PREFIX.format('*')).query(boosting)
        s = s.extra(indices_boost={
            constants.ES_INDEX_PREFIX.format('ja'): 1,
            constants.ES_INDEX_PREFIX.format('en'): 1,
            constants.ES_INDEX_PREFIX.format('un'): 0.5
        })
        # TODO: ATTENTION: EVEN MORE INDEXES CREATED ON LANGUAGE -> PUT ALL TO UN
        s = s.highlight_options(order='score')
        s = s.highlight('body', fragment_size=50)
        s = s.highlight('subject')
        response = s.execute()

        for hit in response:
            if hasattr(hit, 'buildNum'):
                continue
            print(hit.meta.score, hit.langCode, hit.langPercent, '\n', hit.subject)
            if hasattr(hit.meta.highlight, 'body'):
                for fragment in hit.meta.highlight.body:
                    print(fragment)
            if hasattr(hit.meta.highlight, 'subject'):
                for fragment in hit.meta.highlight.subject:
                    print(fragment)

        # Multiple languages: https://www.elastic.co/guide/en/elasticsearch/guide/current/mixed-lang-fields.html
        # Identifying languages: https://www.elastic.co/guide/en/elasticsearch/guide/current/language-pitfalls.html#identifying-language

        return response

    def search_low(self, qterm):
        response = self._es.search(
            index="test-email-index",
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
            print(hit.meta.score,'\n', hit.subject)
            if hasattr(hit, '_highlight.body'):
                for fragment in hit['_highlight.body']:
                    print(fragment)

            if hasattr(hit, '_highlight.subject'):
                for fragment in hit['_highlight.subject']:
                    print(fragment)
        return response


