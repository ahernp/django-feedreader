README
======

Feedreader is a simple Django 1.8 app to aggregate RSS feeds.

Features
--------

-  Locally stored feed link, title and description.
-  Locally stored entry link, title and description.
-  Show recent entries.
-  String search of locally stored data.
-  Uses Django admin to manage feeds.

Detailed documentation is in the "docs" directory. These are available
online `here <http://ahernp.com/media/doc/django-feedreader/>`__.

Quick start
-----------

1. Add "feedreader" to your INSTALLED\_APPS setting like this::

     INSTALLED_APPS = (...
                       'feedreader',
                       )

2. Include the feedreader URLconf in your project urls.py like this::

     url(r'^feedreader/', include('feedreader.urls', namespace='feedreader')),

3. Run ``python manage.py syncdb`` to create the feedreader models.

4. Run ``python manage.py collectstatic`` to copy static files to your
   project's static root.

5. Start the development server and visit
   `/admin/feedreader/feed/ <https://127.0.0.1:8000/admin/feedreader/feed>`__
   to add feeds. Only each feed's xml url is needed.

6. Visit `/feedreader/ <https://127.0.0.1:8000/feedreader/>`__
   to see the contents of the feeds.
   
Feedreader includes support for Django's ``i18n`` Internationalization and
localization functionality. Enable this by adding the Feedreader URLs using
``i18n_patterns`` and including the ``django.middleware.locale.LocaleMiddleware``
in your project's settings.

Dependencies
------------

-  `Django 1.8 <https://pypi.python.org/pypi/Django/1.8>`__
-  `djangorestframework 3.2.2 <http://django-rest-framework.org>`__
-  `django-braces 1.4.0 <https://pypi.python.org/pypi/django-braces/1.4.0>`__
-  `factory_boy 2.5.1 <https://pypi.python.org/pypi/factory_boy/2.5.1>`__
-  `feedparser 5.2.0 <https://pypi.python.org/pypi/feedparser/5.2.0>`__
-  `mock 1.0.1 <https://pypi.python.org/pypi/mock/1.0.1>`__
-  `pytz <https://pypi.python.org/pypi/pytz/2015.2>`__

