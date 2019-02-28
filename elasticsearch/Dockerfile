FROM elasticsearch:5.3.2 
#6.6.0

COPY elasticsearch.yml /etc/elasticsearch/
COPY jvm.options /etc/elasticsearch/
#COPY log4j2.properties /etc/elasticsearch/
#COPY userdict_ja.txt /etc/elasticsearch/
COPY userdict_ja.txt /usr/share/elasticsearch/config/ 
COPY  limits.conf /etc/security/

# Check virtual memory (equals to host, at least 262144)
RUN sysctl vm.max_map_count

RUN bin/elasticsearch-plugin install analysis-kuromoji

