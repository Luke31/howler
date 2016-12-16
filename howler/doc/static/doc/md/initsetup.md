# Initial setup of environment

## Django

    pip install --upgrade pip
    pip install pillow          # Implementation of Pyhton Imaging Library PIL
    
    sudo apt-get install libpq-dev python3-dev  # Prepare PostgreSQL packages for django postgresql driver
    
    pip install psycopg2        # PostgreSQL Adapter
    pip install django-cms      # (3.4.1, Django 1.9.11)
    pip install djangocms-installer
    
    mkdir tutorial-project
    cd tutorial-project
    djangocms -w -f -p . mysite
      # Installs django Filer -f
      # current as parent -p
  
  
  
# SET UP NEW: Old Tutorial:

    django-admin.py startproject dcms
    cd dcms
    python manage.py runserver 0.0.0.0:8000     # TEST-START
    nano dcms/settings.py

* Add on top:

        # -*- coding: utf-8 -*-
        import os
        gettext = lambda s: s
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #If not already in file

* Add to **INSTALLED_APPS**
    
        'cms',     # django CMS itself
        'mptt',    # utilities for implementing a modified pre-order traversal tree
        'menus',   # helper for model independent hierarchical website navigation
        'south',   # intelligent schema and data migrations
        'sekizai', # for javascript and css management
    
* Add to **MIDDLEWARE_CLASSES**

        'cms.middleware.page.CurrentPageMiddleware',
        'cms.middleware.user.CurrentUserMiddleware',
        'cms.middleware.toolbar.ToolbarMiddleware',
        'cms.middleware.language.LanguageCookieMiddleware',
    
* Add to free location:

        TEMPLATE_CONTEXT_PROCESSORS = (
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.i18n',
            'django.core.context_processors.request',
            'django.core.context_processors.media',
            'django.core.context_processors.static',
            'cms.context_processors.media',
            'sekizai.context_processors.sekizai',
        )
    
* Modify `STATIC_ROOT` and `MEDIA_ROOT` to (only `STATIC_URL` already present):

        MEDIA_ROOT = os.path.join(BASE_DIR, "media")
        MEDIA_URL = "/media/"

        STATIC_ROOT = os.path.join(BASE_DIR, "static")
        STATIC_URL = "/static/"
    
* Set:

        TEMPLATE_DIRS = (
            os.path.join(BASE_DIR, "templates"),
        )

        CMS_TEMPLATES = (
            ('template_1.html', 'Template One'),
        )

        LANGUAGES = [ 
        ('en-us', 'English'),
        ]
    
* DB already set
    
* urls.py

        from django.conf.urls.defaults import *
        from django.conf.urls.i18n import i18n_patterns
        from django.contrib import admin
        from django.conf import settings

        admin.autodiscover()

        urlpatterns = i18n_patterns('',
            url(r'^admin/', include(admin.site.urls)),
            url(r'^', include('cms.urls')),
        )

        if settings.DEBUG:
            urlpatterns += patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
            url(r'', include('django.contrib.staticfiles.urls')),
        ) + urlpatterns

* `wally_search/dcms mkdir templates`
* `nano templates/base.html`

        {% load cms_tags sekizai_tags %}
        <html>
          <head>
              {% render_block "css" %}
          </head>
          <body>
              {% cms_toolbar %}
              {% placeholder base_content %}
              {% block base_content %}{% endblock %}
              {% render_block "js" %}
          </body>
        </html>
    
* `nano templates/template_1.html`

        {% extends "base.html" %}
        {% load cms_tags %}

        {% block base_content %}
          {% placeholder template_1_content %}
        {% endblock %}
    
* `python manage.py syncdb --all`
* `manage.py migrate --fake`