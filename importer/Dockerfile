FROM python:3.7
MAINTAINER Negi Corp
#RUN apt-get update
#RUN apt-get -y install git apache2 apache2-utils python3 python3-dev libapache2-mod-wsgi-py3 libpq-dev libffi-dev curl gnupg apache2-dev
#RUN curl -sL https://deb.nodesource.com/setup_9.x | bash - && apt-get install -y nodejs npm
#Use .dockerignore file
ADD requirements.txt /app/
#Should actually separate this python package and django static files -> then only set requirements howler
RUN mkdir -p ~/.ssh && ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts
RUN cd /app/ && pwd && CFLAGS="-Wno-narrowing" pip install -r requirements.txt
ADD index-cmd.py /app/
ADD index-cmd-irc.py /app/
ADD wait-for-it.sh /app/
ADD update-indices.sh /app/

WORKDIR /app/
CMD ["./update-indices.sh"]

