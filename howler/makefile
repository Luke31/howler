install: bin/python

bin/python:
    # virtualenv .
    bin/pip install -r requirements.txt.

serve: bin/python
    bin/python ./manage.py runserver 8888

deploy: bin/python
    bin/python ./manage.py collectstatic --clear --noinput
    touch howler/wsgi.py  # trigger reload

clean:
    rm -rf bin/ lib/ build/ dist/ *.egg-info/ include/ local/