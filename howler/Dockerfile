FROM debian:9.6
MAINTAINER Negi Corp
RUN apt-get update
RUN apt-get -y install git apache2 apache2-utils python3 python3-dev libapache2-mod-wsgi-py3 libpq-dev libffi-dev curl gnupg apache2-dev
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash - && apt-get install -y nodejs npm
RUN npm install -g bower
RUN echo '{ "allow_root": true }' > /root/.bowerrc
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

ADD howler_site.conf /etc/apache2/sites-available/000-default.conf

#RUN sed -i 's,#LoadModule rewrite_module modules/mod_rewrite.so,LoadModule rewrite_module modules/mod_rewrite.so,g' /usr/local/apache2/conf/httpd.conf

RUN cd /var/www/howler && python ./manage.py bower install && \
    django-admin compilemessages && \
    touch wsgi.py && \
    python ./manage.py collectstatic -v0 --noinput
#RUN cd /var/www/howler && python ./manage.py migrate && \   # Run this command after container started
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]
