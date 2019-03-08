FROM elastic/filebeat:5.6.15

COPY filebeat.yml /usr/share/filebeat/filebeat.yml
USER root
RUN chown filebeat /usr/share/filebeat/filebeat.yml
RUN chmod go-w /usr/share/filebeat/filebeat.yml

RUN mkdir /app
RUN chown filebeat /app
USER filebeat
# ADD wait-for-it.sh /app
# ADD wait-for-empty-irc.sh /app
# WORKDIR /app/
# CMD ["./wait-for-empty-irc.sh"]

