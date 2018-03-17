README
======

Feedreader is a simple Django app to aggregate RSS feeds.

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

     path('feedreader/', include('feedreader.urls')),

3. Run ``python manage.py migrate`` to create the feedreader models.

4. Run ``python manage.py collectstatic`` to copy static files to your
   project's static root.

5. Start the development server and visit
   `/admin/feedreader/feed/ <https://127.0.0.1:8000/admin/feedreader/feed>`__
   to add feeds. Only each feed's xml url is needed.

6. Visit `/feedreader/ <https://127.0.0.1:8000/feedreader/>`__
   to see the contents of the feeds.

Dependencies
------------

-  `Django 2.0.3 <https://pypi.python.org/pypi/Django/2.0.3>`__
-  `django-braces 1.12.0 <https://pypi.python.org/pypi/django-braces/1.12.0>`__
-  `factory_boy 2.10.0 <https://pypi.python.org/pypi/factory_boy/2.10.0>`__
-  `feedparser 5.2.1 <https://pypi.python.org/pypi/feedparser/5.2.1>`__
