# howler
Django and Elasticsearch webapp for searching Japanese e-mails and IRC logs.

## Usage
Run `docker-compose up` and access http://localhost:8000 in your browser. This will automatically start all required services, load example e-mails and IRC logs and open the e-mail search.

## Main URLs and services
* Elasticsearch indices: http://localhost:9200/_cat/indices?v
* Kibana Console: http://localhost:5601/app/kibana#/dev_tools/console?_g=()
* Kuromoji synonym test: http://localhost:9200/mailing-ja/_analyze?pretty=true&analyzer=kuromoji_custom&text=%E4%BA%AC%E7%94%A3%E5%A4%A7
* Development documentation: http://localhost:8000/doc/home/

## Prerequisites
* docker
* docker-compose

