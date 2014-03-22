Feedreader
----------

Feedreader is a simple Django 1.6 app to aggregate RSS feeds.

Features
--------

-  Locally stored feed link, title and description.
-  Locally stored entry link, title and description.
-  Show recent entries.
-  String search of locally stored data.
-  Uses Django admin to manage feeds.

Detailed documentation is in the "docs" directory. These are available
online `here <http://ahernp.com/static/doc/django-feedreader/>`__.

Quick start
-----------

1. Add "feedreader" to your INSTALLED\_APPS setting like this::

     INSTALLED\_APPS = ( ... 'feedreader', )

2. Include the feedreader URLconf in your project urls.py like this::

     url(r'^feedreader/', include('feedreader.urls')),

3. Run ``python manage.py syncdb`` to create the feedreader models.

4. Run ``python manage.py collectstatic`` to copy static files to your
   project's static root.

5. Start the development server and visit
   http://127.0.0.1:8000/admin/feedreader/feed to add feeds. Only each
   feed's xml url is needed.

6. Visit http://127.0.0.1:8000/feedreader/ to see the contents of the
   feeds.

Dependencies
------------

-  `Django 1.6.2 <https://pypi.python.org/pypi/Django/1.6.2>`__
-  `feedparser <https://pypi.python.org/pypi/feedparser>`__
-  `pytz <https://pypi.python.org/pypi/pytz/2013.9>`__

