#!/usr/bin/env python3
import os
import argparse
from wally.elastic.index import Index
from elasticsearch import Elasticsearch
from wally.elastic import constants


def update(args):
    es = Elasticsearch([args.host], timeout=args.timeout, maxsize=args.maxcon)
    index = Index(es, es_index_prefix=args.indexprefix, es_type_name=args.type)
    kuromoji_synonyms = ['京産大, 京都産業大学', '京都大学, 京大']
    index.add_mapping_to_index_multi(delete_old_indices=args.force, kuromoji_synonyms=kuromoji_synonyms)

    summary = index.index_bulk_from_dir(os.getcwd())
    print("Successfully indexed {0}/{1} emails. Errors on json-convert: {2}, Errors in indexing: {3}".format(
        summary.cnt_success, summary.cnt_total, len(summary.errors_convert), len(summary.errors_index)))


parser = argparse.ArgumentParser()
# parser.add_argument('--version', action='version', version='1.0.1')
subparsers = parser.add_subparsers()

update_parser = subparsers.add_parser('update')
update_parser.add_argument('host', help='Elasticsearch host e.g. 10.0.10.180 or 10.0.10.180:9200')
update_parser.add_argument('--maxcon', default=25, help='Elasticsearch max number of connections to node')
update_parser.add_argument('--timeout', default=30, help='Elasticsearch connection timeout in seconds e.g. 30')
update_parser.add_argument('--indexprefix', default='mailing-{0}',
                           help='Elasticsearch index-prefix e.g. "mailing-{0}", {0} replaced by lang-code')
update_parser.add_argument('--type', default='email', help='Elasticsearch email-type e.g. email')
update_parser.add_argument('--force', action='store_true',
                           help='Force update all emails (Deletes existing indices, synonyms must be re-loaded from website)')
update_parser.set_defaults(func=update)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # call the default function
