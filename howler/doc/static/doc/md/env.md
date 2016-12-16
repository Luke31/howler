# Production environment

Following production environment has been set up:

## Production server
* Debian 8.6 (Jessie)
#### Users

|User|Password|
|---|---|
|lukas|hogehoge|
|ssh-key password|hogehoge|

    
### Apache 2 (2.4.10) 
* Service-name: `apache2`
* Port: 80
* Users: wwwd-data (Also member of elasticsearch to modify user-dict)
* Restart: `sudo /etc/init.d/apache2 restart`
### postgresql (9.4.9) 
* Service-name: `postgresql`
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

### elasticsearch (?)
* Service-name: `elasticsearch`
* Port: 9200
* User: elasticsearch

**View indexes:** [http://10.0.10.180:9200/_cat/indices?v](http://10.0.10.180:9200/_cat/indices?v)
### kibana
* Service-name: `kibana`
* Port: 5601
* including Sense/Console
* User: kibana

* Filesystem:
    * /var/www/howler
    * /var/git/lukas-sandbox