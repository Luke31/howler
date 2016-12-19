# Production environment

Following production environment has been set up:

## Production server
* Debian 8.6 (Jessie)
* IP: `10.0.10.180`
* CPU: 4 Cores
* Storage: ~990Gb
* Memory: 16Gb
    * 6Gb fix allocated to elasticsearch (mainly `htop` green) - See: [Elasticsearch - Heap: Sizing and Swapping](https://www.elastic.co/guide/en/elasticsearch/guide/current/heap-sizing.html)
    * Rest mainly used by OS cached Lucene-files (mainly `htop` orange) - See: [Elasticsearch - Give (less than) Half Your Memory to Lucene](https://www.elastic.co/guide/en/elasticsearch/guide/current/heap-sizing.html#_give_less_than_half_your_memory_to_lucene)
* Java 8 (OpenJDK x64 1.8.0_111)

#### Users

|User|Password|
|---|---|
|lukas|hogehoge|
|ssh-key password|hogehoge|
|saita|hogehoge2|
|django|django|

#### Ports

|Port|Service|
|---|---|
|80|`apache2`|
|5432|`postgresql`|
|9200|`elasticsearch`|
|5601|`kibana`|

### Postgresql (9.4.9) 
* Service-name: `postgresql`
* Port:  5432
* Service-user: `postgresql` (No password entry)
* Access: `local all trust`
#### Users

|User|Password|
|---|---|
|postgres|[none]|
|lukas|hogehoge|
|django|django|

#### Databases

|Name|Owner|
|---|---|
|django|django|

### Elasticsearch (5.0.1)
* Service-name: `elasticsearch`
* Port: 9200
* Service-user: elasticsearch
#### Filesystem

|Purpose|File|
|---|---|
|Config|`/etc/elasticsearch/elasticsearch.yml`| 
|Log|`/var/log/elasticsearch/wally-prod.log`|
|JVM options (Heap size)|`/etc/elasticsearch/jvm.options`|
|Log properties|`/etc/elasticsearch/log4j2.properties`|
|User dictionary Kuromoji|`/etc/elasticsearch/userdict_ja.txt`|
|Shared files (e.g. plugins such as Kuromoji)|`/usr/share/elasticsearch/`|

**Elasticsearch indices:** [http://10.0.10.180:9200/_cat/indices?v](http://10.0.10.180:9200/_cat/indices?v)
### Kibana (5.0.1)
* Service-name: `kibana`
* Port: 5601
* including Sense/Console
* Service-user: kibana
#### Filesystem
|Purpose|File|
|---|---|
|Log error|`/var/log/kibana/kibana.stderr`|
|Log out|`/var/log/kibana/kibana.stdout`|

**Kibana Dev Tools Console:** [http://10.0.10.180:5601/app/kibana#/dev_tools](http://10.0.10.180:5601/app/kibana#/dev_tools)

### Apache 2 (2.4.10) 
* Service-name: `apache2`
* Port: 80
* Service-user: `wwwd-data` (No password entry, Also member of elasticsearch to modify user-dict)
* Restart: `sudo /etc/init.d/apache2 restart`
* Uses system Python 3.4.2 (`python3` and `pip3`)
* Uses `libapache2-mod-wsgi-py3` to run Django applications
#### Filesystem
|Purpose|File|
|---|---|
|Enabled sites|`/etc/apache2/sites-enabled/`|
|Log error (rolling)|`/var/log/apache2/error.log`|
|Website root|`/var/www/`|

### Howler (Django application)
* Running on Apache2
* Logs to apache-log

#### Django Superusers (May enter Admin-area)

|User|Password|
|---|---|
|lukas|hogehoge|

#### Filesystem
|Purpose|File|
|---|---|
|Deployment target dir Howler (Django) apache2 webapplication|`/var/www/howler/`|
|Howler (Django) settings|`/var/www/howler/howler/settings.py`|
|Pre-deployment directory git repository|`/var/git/lukas-sandbox/howler/`|

**Hint:** To view django's 500 internal server errors on the clientside, enable debug in Howler's settings:

    DEBUG = True
