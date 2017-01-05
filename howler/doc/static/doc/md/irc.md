# IRC Logstash

For the IRC and syslog analysis, the Elastic stack (former known as ELK Stack) is used. For this Logstash has been additionally installed on the server.

Following pipeline is used:

    [Server with logs (IRC/syslog etc.] 
        Filebeat - read logs and sends to logstash-server
          v
    [Production server 10.0.10.180]
        Logstash - filters logs and indexes them in elasticsearch
          v
        Elasticsearch - holds logs for analysis
          v
        Kibana - visually analyze logs

The description for the setup of Logstash, Elasticstash and Kibana is described here: [Production Environment initial setup](/howler/doc/done/)
Following is the 

## Filebeat setup
To read the logs on the client and send them to the logstash server, Filebeat is used. 

* Installation: [Step 1: Installing Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html)

* Config: `/etc/filebeat/filebeat.yml` or `C:\Program Files\Filebeat\filebeat.yml`

    [Filebeat Prospectors Configuration format](https://www.elastic.co/guide/en/beats/filebeat/current/configuration-filebeat-options.html)

        filebeat.prospectors:
        - input_type: log
          paths:
            - /home/saita/archive/irc/*.txt
            #- /var/log/*.log
            #- c:\programdata\elasticsearch\logs\*
          encoding: iso-2022-jp
        
        #- input_type: log
        #  paths:
        #    - c:\Users\Lukas\AppData\Roaming\X-Chat 2\xchatlogs\IRC Kyoto-#co-conv.log
            
        #-------------------------- Elasticsearch output ------------------------------
        #output.elasticsearch:
          # Array of hosts to connect to.
          #hosts: ["localhost:9200"]
            
        #----------------------------- Logstash output --------------------------------
        output.logstash:
          # The Logstash hosts
          hosts: ["localhost:5043"]
          #hosts: ["10.0.10.180:5043"]
          
* Starting Filebeat: [Step 5: Starting Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-starting.html)

    * deb: `sudo /etc/init.d/filebeat start`
        
    * win: `PS C:\Program Files\Filebeat> Start-Service filebeat`
    
* Log: `/var/log/filebeat/filebeat`
    
* Filebeat remembers the last read position of the log-files in its registry: `/var/lib/filebeat/registry` or `c:\ProgramData\filebeat\registry`
    
    Delete this file if you would like to reset the position.