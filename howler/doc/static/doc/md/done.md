# Done stuff

-Java 8
-Elasticsearch (License: Apache-2.0 https://tldrlegal.com/license/apache-license-2.0-(apache-2.0))
-pyenv
-pyenv-virtualenv
3844
-elasticsearch
-elasticsearch-dsl
-kibana (sense/console)
-pip install cld2-cffi

-Java 8:
/etc/apt/sources.list.d/ debian-jessie-backports.list

	# jessie-backports main for openjdk-8-jdk
	deb http://ftp.debian.org/debian jessie-backports main

/etc/apt/preferences.d/debian-jessie-backports

	Package: *
	Pin: release o=Debian,a=jessie-backports
	Pin-Priority: -200
	
sudo update-alternatives --config java

----------
--Elasticsearch 5.0.1 Port 9200 (https://www.elastic.co/guide/en/elasticsearch/reference/5.0/deb.html)
----------

--SERVICE
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable elasticsearch.service

sudo systemctl start elasticsearch.service
sudo systemctl stop elasticsearch.service

-journalctl NOT enabled

--CONFIG /etc/elasticsearch/elasticsearch.yml:
cluster.name: wally-prod
node.name: node-wally-1
bootstrap.memory_lock: true #no swapping

Access:
network.host: 10.0.10.180
network.port: 9200

--Set virtual memory
sysctl -w vm.max_map_count=262144

--CONFIG JVM Set JVM system properties heap size /etc/elasticsearch/jvm.options
-Xms6g 
-Xmx6g 

--Set user limits /etc/security/limits.conf
# allow user 'elasticsearch' mlockall
elasticsearch   soft    memlock unlimited
elasticsearch   hard    memlock unlimited

--Uncomment in /usr/lib/systemd/system/elasticsearch.service
LimitMEMLOCK=infinity

----------
--KIBANA 5.0.1 Port 5601 (https://www.elastic.co/guide/en/kibana/current/deb.html)
----------

--SERVICE
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable kibana.service

sudo systemctl start kibana.service
sudo systemctl stop kibana.service

--CONFIG (/etc/kibana/kibana.yml - no log)
server.port: 5601
server.host: 10.0.10.180
server.name: wally-prod-kibana
#server.defaultRoute: /app/kibana
#elasticsearch.url: http://localhost:9200
elasticsearch.url: "http://10.0.10.180:9200"

----------
--KUROMOJI (https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-kuromoji.html)
----------
--Install in /usr/share/elasticsearch
sudo bin/elasticsearch-plugin install analysis-kuromoji

----------
--Apache 2
----------
sudo apt-get install python3-dev
sudo apt-get install apache2
sudo apt-get install virtualenv
sudo apt-get install libapache2-mod-wsgi-py3

--CONFIG /etc/apache2/sites-available/001-howler.conf
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

--in /var/www/howler
pyenv virtualenv 3.5.2 howler
source bin/activate
pip3 (3.4.2) install django-bower

--RESTART
sudo a2ensite 001-howler

--DEPLOYMENT
cd /var/git/lukas-sandbox
git pull
cp -r /var/git/lukas-sandbox/howler/ /var/www/

sudo /etc/init.d/apache2 restart

--Superuser
python manage.py createsuperuser

----------
--Postgresql
----------
sudo apt-get install libpq-dev postgresql postgresql-contrib
-Added user lukas/django and granted local permission (/etc/postgresql/9.4/main/pg_hba.conf)

local   all             all                                     trust
local   all             django                                  ident

sudo /etc/init.d/postgresql restart

sudo su postgres
psql django

CREATE ROLE django LOGIN
  ENCRYPTED PASSWORD 'md5f77cf19ca83d94461f3d5797ae873f6b'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
  
ALTER USER django WITH PASSWORD 'django';

pip install psycopg2
pip3 install psycopg2


----------
--Fabric3 (https://pypi.python.org/pypi/Fabric3/1.10.2)
----------

----------
--Errors
----------
Internal server error 500
-Update wally on server for 3.4.2 pip3?
