#!/usr/bin/env bash
./wait-for-it.sh elasticsearch:9200 -- python index-cmd-irc.py update elasticsearch --force
python index-cmd.py update /datain/mail elasticsearch --force

