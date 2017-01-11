#!/usr/bin/env python3
import os
import argparse
from wally.elastic.index import IndexIrc
from elasticsearch import Elasticsearch
from wally.elastic import constants
from argparse import RawTextHelpFormatter

"""Command-line interface to update elasticsearch IRC index mapping
--How to install this package for script-usage--
1. Install pip3:
sudo apt-get install python3-pip

2. Download this package with its script:
git clone ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git
or just copy it to any directory

3. Go to installed directory -> project wally
cd lukas-sandbox/wally

3. Install the required python modules (You may also create a virtualenv for this):
pip3 install -r requirements.txt

--How to use this script to get help--
python3 index-cmd-irc.py -h
python3 index-cmd-irc.py update -h
"""
version = '1.0.3'


def update(args):
    """
    Updates elasticsearch IRC index mapping
    :param args:
    :return:
    """
    es = Elasticsearch([args.estargethost], timeout=args.timeout, maxsize=args.maxcon)
    index = IndexIrc(es, es_index_prefix=args.indexprefix, es_type_name=args.doctype)
    if args.force:
        kuromoji_synonyms = ['京都産業大学, 京産大', '京都大学, 京大']
    else:
        kuromoji_synonyms = []

    if args.force:
        print('Deleting old indices, deleting irc logs, creating new indices with new default synonyms...')
    else:
        print("Updating existing indices (without deleting existing irc logs and synonyms)...")
    index.add_mapping_to_index('', constants.SUPPORTED_LANG_CODES_ANALYZERS['ja'], delete_old_indices=args.force,
                               kuromoji_synonyms=kuromoji_synonyms)

    print("Updated mapping for IRC logs index")


description = \
    'Update elasticsearch IRC index mapping.\n\n' \
    'Example usage:\n' \
    '-Update index mapping to es-server:\n' \
    'python3 index-cmd-irc.py update 10.0.10.180\n\n' \
    '-Update force update IRC index mapping to es-server with (deletes existing indices):\n' \
    'python3 index-cmd-irc.py update 10.0.10.180 --force\n\n' \
    'Make sure the required python modules are installed, if not run:\n' \
    'pip3 install -r requirements.txt\n\n'

parser = argparse.ArgumentParser(
    description=description,
    epilog='epilog', formatter_class=RawTextHelpFormatter)
parser.add_argument('--version', action='version', version=version)
subparsers = parser.add_subparsers()
update_parser = subparsers.add_parser('update')
update_parser.add_argument('estargethost',
                           help='Elasticsearch host with/without port e.g. 10.0.10.180:9200 [default: 10.0.10.180]')
update_parser.add_argument('--force', action='store_true',
                           help='Force update IRC index mapping (Deletes existing indices, synonyms must be re-loaded from website)')
update_parser.add_argument('--maxcon', default=25, help='Elasticsearch max number of connections to node [default: 25]')
update_parser.add_argument('--timeout', default=30, help='Elasticsearch connection timeout in seconds [default: 30]')
update_parser.add_argument('--indexprefix', default='logstash-irc{0}',
                           help='Elasticsearch index-prefix [default: "logstash-irc{0}"], {0} replaced by empty string')
update_parser.add_argument('--doctype', default='irclog', help='Elasticsearch irc-doctype [default: "irclog"]')
update_parser.set_defaults(func=update)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # call the default function
