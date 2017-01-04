#!/usr/bin/env python3
import os
import argparse
from wally.elastic.index import Index
from elasticsearch import Elasticsearch
from wally.elastic import constants
from argparse import RawTextHelpFormatter

"""Command-line interface to update elasticsearch index with new emails
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
python3 index-cmd.py -h
python3 index-cmd.py update -h
"""
version = '1.0.3'


def update(args):
    """
    Updates elasticsearch index with new emails
    :param args:
    :return:
    """
    es = Elasticsearch([args.estargethost], timeout=args.timeout, maxsize=args.maxcon)
    index = Index(es, es_index_prefix=args.indexprefix, es_type_name=args.doctype)
    if args.force:
        kuromoji_synonyms = ['京都産業大学, 京産大', '京都大学, 京大']
    else:
        kuromoji_synonyms = []

    print('Existing emails in index: {0}'.format(len(index.already_imported_ids)))
    if args.force:
        print('Deleting old indices, deleting emails, creating new indices with new default synonyms...')
    else:
        print("Updating existing indices (without deleting existing emails and synonyms)...")
    index.add_mapping_to_index_multi(delete_old_indices=args.force, kuromoji_synonyms=kuromoji_synonyms)

    if os.path.isdir(args.src):
        print('Import new emails from directory: {0} ...'.format(args.src))
        srcdir = args.src
        summary = index.index_bulk_from_dir(srcdir, ignore_already_imported=not args.force)
    else:
        print('Import single new email: {0} ...'.format(args.src))
        files = [args.src]  # Only one file in list
        summary = index.index_bulk_from_files(files)

    if summary.errors_convert:
        print('Errors during conversion:')
        for err in summary.errors_convert:
            print(err)
    if summary.errors_index:
        print('Errors during indexation:')
        for err in summary.errors_index:
            print(err)
    print("Successfully indexed {0}/{1} emails. Errors on json-convert: {2}, Errors in indexing: {3}".format(
        summary.cnt_success, summary.cnt_total, len(summary.errors_convert), len(summary.errors_index)))


description = \
    'Update elasticsearch index with one or many new emails.\n\n' \
    'Example usage:\n' \
    '-Update new mails in folder to es-server (for Cron):\n' \
    'python3 index-cmd.py update data_in 10.0.10.180\n\n' \
    '-Update force all mails in folder to es-server with (deletes existing indices):\n' \
    'python3 index-cmd.py update data_in 10.0.10.180 --force\n\n' \
    '-Single mail file to es-server:\n' \
    'python3 index-cmd.py update data_in/99992 10.0.10.180\n\n' \
    'Make sure the required python modules are installed, if not run:\n' \
    'pip3 install -r requirements.txt\n\n'

parser = argparse.ArgumentParser(
    description=description,
    epilog='epilog', formatter_class=RawTextHelpFormatter)
parser.add_argument('--version', action='version', version=version)
subparsers = parser.add_subparsers()
update_parser = subparsers.add_parser('update')
update_parser.add_argument('src', help='src folder of emails OR email filename')
update_parser.add_argument('estargethost',
                           help='Elasticsearch host with/without port e.g. 10.0.10.180:9200 [default: 10.0.10.180]')
update_parser.add_argument('--force', action='store_true',
                           help='Force update all emails (Deletes existing indices, synonyms must be re-loaded from website)')
update_parser.add_argument('--maxcon', default=25, help='Elasticsearch max number of connections to node [default: 25]')
update_parser.add_argument('--timeout', default=30, help='Elasticsearch connection timeout in seconds [default: 30]')
update_parser.add_argument('--indexprefix', default='mailing-{0}',
                           help='Elasticsearch index-prefix [default: "mailing-{0}"], {0} replaced by lang-code')
update_parser.add_argument('--doctype', default='email', help='Elasticsearch email-doctype [default: "email"]')
update_parser.set_defaults(func=update)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # call the default function
