# Production environment

Following production environment has been set up:

## Production server
* Debian 8.6 (Jessie)
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

### postgresql (9.4.9) 
* Service-name: `postgresql` (No password entry)
* Port:  5432
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

### elasticsearch (5.0.1)
* Service-name: `elasticsearch`
* Port: 9200
* Service-user: elasticsearch
* Filesystem:

|Purpose|File|
|---|---|
|Config|`/etc/elasticsearch/elasticsearch.yml`| 
|Log|`/var/log/elasticsearch/wally-prod.log`|
|JVM options (Heap size)|`/etc/elasticsearch/jvm.options`|
|Log properties|`/etc/elasticsearch/log4j2.properties`|
|User dictionary Kuromoji|`/etc/elasticsearch/userdict_ja.txt`|
|Shared files (e.g. plugins)|`/usr/share/elasticsearch`|

**Elasticsearch indices:** [http://10.0.10.180:9200/_cat/indices?v](http://10.0.10.180:9200/_cat/indices?v)
### kibana (5.0.1)
* Service-name: `kibana`
* Port: 5601
* including Sense/Console
* Service-user: kibana
* Filesystem:
    * `/var/www/howler`
    * `/var/git/lukas-sandbox`
    
|Purpose|File|
|---|---|
|Log error|`/var/log/kibana/kibana.stderr`|
|Log out|`/var/log/kibana/kibana.stdout`|

**Kibana Dev Tools Console:** [http://10.0.10.180:5601/app/kibana#/dev_tools](http://10.0.10.180:5601/app/kibana#/dev_tools)

### Apache 2 (2.4.10) 
* Service-name: `apache2`
* Port: 80
* Service-user: `wwwd-data` (No password entry, Also member of elasticsearch to modify user-dict)
* Log: 
* Restart: `sudo /etc/init.d/apache2 restart`
* Uses system Python 3.4.2 (`python3` and `pip3`)
* Uses `libapache2-mod-wsgi-py3` to run Django applications

|Purpose|File|
|---|---|
|Enabled sites|`/etc/apache2/sites-enabled/`|
|Log error (rolling)|`/var/log/apache2/error.log`|
|Website root|`/var/www/`|

### Howler (Django webapplication)
* Apache2 webapplication
* Logs to apache-log

|Purpose|File|
|---|---|
|Deployment repository on server (Temp)|``|
|Howler (Django) apache2 webapplication|`/var/www/howler`|
|Howler (Django) settings|`/var/www/howler/howler/settings.py`|

**Hint:** To view django's 500 internal server errors on the clientside, enable debug in Howler's settings:

    DEBUG = True
