FROM httpd:2.4
MAINTAINER Negi Corp
RUN apt-get update
RUN apt-get -y install git python3 python3-dev libapache2-mod-wsgi-py3 libpq-dev libffi-dev curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash - && apt-get install -y nodejs npm
RUN npm install -g bower
RUN rm /usr/bin/python

RUN ln /usr/bin/python3 /usr/bin/python
RUN apt-get -y install python3-pip
RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
#Use .dockerignore file
ADD requirements.txt /var/www/howler/
#Should actually separate this python package and django static files -> then only set requirements howler
RUN mkdir -p ~/.ssh && ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts
RUN cd /var/www/howler && pwd && CFLAGS="-Wno-narrowing" pip install -r requirements.txt
ADD . /var/www/howler/

ADD ./howler.conf /etc/apache2/sites-available/000-default.conf

RUN cd /var/www/howler && python ./manage.py bower install \
    django-admin compilemessages && \
    touch wsgi.py
#python ./manage.py collectstatic -v0 --noinput && \
#python ./manage.py migrate && \
#RUN /etc/init.d/apache2 restart

#COPY templates/index_dashboard.html /var/www/html/
#CMD ["httpd-foreground"]
#CMD ["sh"]
EXPOSE 80 3500