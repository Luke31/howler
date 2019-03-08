FROM elastic/filebeat:5.6.15

COPY filebeat.yml /usr/share/filebeat/filebeat.yml
USER root
RUN chown filebeat /usr/share/filebeat/filebeat.yml
RUN chmod go-w /usr/share/filebeat/filebeat.yml

ADD wait-for-empty-irc.sh /usr/share/filebeat/

USER filebeat
CMD ["./wait-for-empty-irc.sh"]

