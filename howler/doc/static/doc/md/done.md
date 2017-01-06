# Production Environment initial setup
Here the initial setup of the production environment (10.0.10.180) is described.

##Java 8 Installation:
Debian 8.6 (Jessie) officially doesn't support Java 8, but a backport is available:

* Add Backport: `nano /etc/apt/sources.list.d/debian-jessie-backports.list`

        # jessie-backports main for openjdk-8-jdk
        deb http://ftp.debian.org/debian jessie-backports main

* Enable Backport: `nano /etc/apt/preferences.d/debian-jessie-backports`

        Package: *
        Pin: release o=Debian,a=jessie-backports
        Pin-Priority: -200
	
* Select new Java version:
`sudo update-alternatives --config java`

##Elasticsearch 5.0.1 (Port 9200) 
* Installation tutorial for Debian: [Install elasticsearch with debain ](https://www.elastic.co/guide/en/elasticsearch/reference/5.0/deb.html)

* Service Start/Stop

        sudo /bin/systemctl daemon-reload
        sudo /bin/systemctl enable elasticsearch.service
 
        sudo systemctl start elasticsearch.service
        sudo systemctl stop elasticsearch.service

**Hint:** journalctl NOT enabled

* Config `/etc/elasticsearch/elasticsearch.yml:`

        cluster.name: wally-prod
        node.name: node-wally-1
        bootstrap.memory_lock: true # no swapping
        
        Access:
        # network.host: 10.0.10.180
        network.bind_host: ["10.0.10.180", "localhost"] # Also enable access EL locally
        network.publish_host: 10.0.10.180
        network.port: 9200
        
        # Set virtual memory
        sysctl -w vm.max_map_count=262144

* JVM system properties heap size: `/etc/elasticsearch/jvm.options`

        -Xms6g 
        -Xmx6g 

* Set user limits `/etc/security/limits.conf`

        # allow user 'elasticsearch' mlockall
        elasticsearch   soft    memlock unlimited
        elasticsearch   hard    memlock unlimited

* Uncomment in `/usr/lib/systemd/system/elasticsearch.service`

        LimitMEMLOCK=infinity

##Kibana 5.0.1 (Port 5601) 
To run queries on elasticsearch from the browser or visually analyze your data, Kibana is very helpful. (Former known as Sense)
* Installation tutorial for Debian: [Install Kibana with Debian Package](https://www.elastic.co/guide/en/kibana/current/deb.html)

* Service Start/Stop

        sudo /bin/systemctl daemon-reload
        sudo /bin/systemctl enable kibana.service
        
        sudo systemctl start kibana.service
        sudo systemctl stop kibana.service

* Config: `/etc/kibana/kibana.yml` - no log

        server.port: 5601
        server.host: 10.0.10.180
        server.name: wally-prod-kibana
        #server.defaultRoute: /app/kibana
        #elasticsearch.url: http://localhost:9200
        elasticsearch.url: "http://10.0.10.180:9200"

##Kuromoji
* Elasticsearch plugin website: [Japanese (kuromoji) Analysis Plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-kuromoji.html)

* Install in `/usr/share/elasticsearch/`

        sudo bin/elasticsearch-plugin install analysis-kuromoji

##Apache 2
* Install

        sudo apt-get install python3-dev
        sudo apt-get install apache2
        sudo apt-get install virtualenv
        sudo apt-get install libapache2-mod-wsgi-py3

* Disable existing enabled site by renaming it in: `/etc/apache2/sites-enabled/`
 
        mv 000-default.conf 000-default.conf.disabled

* Config of website: `/etc/apache2/sites-available/001-howler.conf` (Enabled: `/etc/apache2/sites-enabled/001-howler.conf`)

        WSGIPythonPath /var/www/howler
        
        <VirtualHost *:80>
            ServerName howler
            ServerAdmin lukas.m.schmid@gmail.com
            ErrorLog ${APACHE_LOG_DIR}/djangoserver-errors.log
            RedirectMatch ^/$ /howler/
            Alias /static/ /var/www/howler/public/static/
            <Directory /var/www/howler/public/static>
                Order deny,allow
                Allow from all
            </Directory>
            WSGIScriptAlias /howler /var/www/howler/howler/wsgi.py
            <Directory /var/www/howler/howler/>
                <Files wsgi.py>
                Order deny,allow
                Allow from all
                </Files>
            </Directory>
        </VirtualHost>

* Install `django-bower` in `/var/www/howler/` to manage client-side packages

        pyenv virtualenv 3.5.2 howler
        source bin/activate
        pip3 (3.4.2) install django-bower

* Restart site

        sudo a2ensite 001-howler

* Deployment, see: [Home - Deployment](/howler/doc/home/)

* Create a django superuser. Enables log-in for Admin-area of Django-application
        
        python manage.py createsuperuser

##Postgresql
* Install

        sudo apt-get install libpq-dev postgresql postgresql-contrib
    
* Config: `/etc/postgresql/9.4/main/pg_hba.conf`
    
    Add user `lukas` and `django` and grant local permission

        local   all             all                                     trust
        local   all             django                                  ident
        
* Restart
    
        sudo /etc/init.d/postgresql restart
    
* Create django role

    * Switch to postgres user

            sudo su postgres
            psql django
    
    * Create django role

            CREATE ROLE django LOGIN
              ENCRYPTED PASSWORD 'md5f77cf19ca83d94461f3d5797ae873f6b'
              NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
              
            ALTER USER django WITH PASSWORD 'django';
       
* Install postgresql python driver

        pip install psycopg2
        pip3 install psycopg2

##Fabric3 for deployment
Fabric is a simple, Pythonic tool for remote execution and deployment

* Install from pypi: [Fabric3 1.10.2](https://pypi.python.org/pypi/Fabric3/1.10.2)
    
        pip install fabric3

##Logstash 5.1.1 (Port 5043) 
To analyze logs (IRC, syslog etc.) we use Logstash. This completes the [Elastic stack](https://www.elastic.co/v5) (Former known as ELK stack) consisting of: **E**lasticsearch, **L**ogstash, **K**ibana (And Filebeats - former known as Logstash-forwarder)
* Installation tutorial for Debian: [Installing Logstash - Installing from Package Repositories](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html#package-repositories)

* Service Start/Stop

        sudo /bin/systemctl daemon-reload
        sudo /bin/systemctl enable logstash.service
        
        sudo systemctl start logstash.service
        sudo systemctl stop logstash.service
        sudo systemctl restart logstash.service

* Config: `/etc/logstash/logstash.yml`

        node.name: node-wally-log-1
        path.data: /var/lib/logstash
        pipeline.workers: 2
        path.config: /etc/logstash/conf.d
        path.logs: /var/log/logstash

* JVM system properties heap size: `/etc/logstash/jvm.options`

        -Xms256m
        -Xmx1g

* IRC-Log Pipeline config: `/etc/logstash/conf.d/10-irc-log-filter.conf`
    
    
    
        input {
            beats {
                port => "5043"
            }
        }
        filter {
            grok {
                match => {
                    "message" => [ "%{HOUR:hour}%{MINUTE:minute}%{SECOND:second} \<\#%{GREEDYDATA:channel}:%{USERNAME:username}\> %{GREEDYDATA:msg}",
                                   "%{HOUR:hour}%{MINUTE:minute}%{SECOND:second} \>\#%{GREEDYDATA:channel}\< \*%{GREEDYDATA:username}\* %{GREEDYDATA:msg}"] 
                }
                # break_on_match => false
            }
            if "_grokparsefailure" in [tags] { # or "_dateparsefailure" in [tags]
                drop { } # Ignore system logs (e.g. "*** CLIENT No.9143 authorized ***")
            }
            grok {
                match => {
                    "source" => [ "%{UNIXPATH:location}\/%{POSINT:date}" ]
                }
            }
            mutate {
                add_field => { "message_timestamp" => "%{date};%{hour}%{minute}%{second}" }
            }
            date {
                match => [ "message_timestamp", "YYYYMMdd;HHmmss" ]
                target => "@timestamp"
            }
            mutate {
                remove_field => [ "message_timestamp", "date", "hour", "minute", "second" ]
            }
        }
        elasticsearch {
            hosts => [ "localhost:9200" ]
            index => "logstash-irc"
            # index => "logstash-%{+YYYY.MM.dd}"
        }


