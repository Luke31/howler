FROM logstash:5.6.15

COPY logstash.yml /etc/logstash/
COPY jvm.options /etc/logstash/
COPY 10-irc-log-filter.conf /etc/logstash/conf.d/

