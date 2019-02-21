# IRC Logstash

For the IRC and syslog analysis, the Elastic stack (former known as ELK Stack) is used. For this Logstash has been additionally installed on the server.

Following pipeline is used:

    [Server with logs (IRC/syslog etc.)] (currently same as production server 10.0.10.180) 
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
          document_type: log
          encoding: euc-jp
          close_*: 5m
          harvester_limit: 600 # parallel open file-handles
          
        
        #- input_type: log
        #  paths:
        #    - c:\Users\Lukas\AppData\Roaming\X-Chat 2\xchatlogs\IRC Kyoto-#example.log
            
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
    
    ##### Don't run the Filebeat service before you haven't created the index using the "IRC Index creation Script" described below. 
    
    ##### Alternatively, you may use the [Update synonyms to elasticsearch indices (Mail and IRC)]-button in the [Settings](/howler/settings/synonym/) page to create/update the index.

    * deb: `sudo /etc/init.d/filebeat start`
            
    * deb service:
    
            sudo systemctl start filebeat.service
            sudo systemctl stop filebeat.service
        
    * win: `PS C:\Program Files\Filebeat> Start-Service filebeat`
    
    
* Log: `/var/log/filebeat/filebeat`
    
* Filebeat remembers the last read position of the log-files in its registry: `/var/lib/filebeat/registry` or `c:\ProgramData\filebeat\registry`
    
    Delete this file if you would like to reset the position. E.g. `sudo rm /var/lib/filebeat/registry`

# IRC Index creation Script
To create the index that holds the IRC logs, we don't rely on Logstash. Please use the script `index-cmd-irc.py` to initially create the IRC log index.
The installation is the same as the [Email Import Script](/howler/doc/importscript/).

**Don't** run the Filebeat service before you haven't created the index using this script.

##How to use the script to get help
    python3 index-cmd-irc.py -h
    python3 index-cmd-irc.py update -h

## Basic usage (also visible when calling the help)
* Update index mapping to es-server `10.0.10.180`:

        python3 index-cmd-irc.py update 10.0.10.180
        
* Update force update IRC index mapping to es-server `10.0.10.180` with (deletes existing index):

        python3 index-cmd-irc.py update 10.0.10.180 --force
        
