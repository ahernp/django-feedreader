==========
Feedreader
==========

Feedreader is a simple Django app to aggregate RSS feeds.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "feedreader" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'feedreader',
      )

2. Include the polls URLconf in your project urls.py like this::

      url(r'^feedreader/', include('feedreader.urls')),

3. Run `python manage.py syncdb` to create the feedreader models.

4. Run `python manage.py collectstatic` to copy static files to your 
   project's static root.

5. Start the development server and visit 
   http://127.0.0.1:8000/admin/feedreader/feed to add feeds. 
   Only each feed's xml url is needed.

6. Visit http://127.0.0.1:8000/feedreader/ to see the contents of the feeds.
