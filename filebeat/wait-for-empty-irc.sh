#!/usr/bin/env bash
./wait-for-it.sh elasticsearch:9200 -- filebeat
# http://localhost:9200/irclogs/_count
