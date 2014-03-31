.. _overview:

Overview
========

Django Feedreader is a web application built using the
`Django <http://www.djangoproject.com/>`_ framework.
It enables users to aggregate the contents of RSS feeds.

The link, title and descriptions of each feed and recent feed entries
are saved in the database.

A `poll_fields <code.html#commands>`_
Django command is included which can be run on a regular basis using
``cron`` or some other scheduling mechanism to keep the local database
of recent entries up to date.

.. index:: Sample Feedreader Output

Sample Output
-------------

.. _image-sample-output:
.. image:: _static/feed_output.png
    :alt: sample feedreader output

.. index:: Requirements

Requirements
------------

Feedreader has been tested using:

* `Django 1.6.1 <https://pypi.python.org/pypi/Django/1.6.1>`_
* `Feedparser 5.1.3 <https://pypi.python.org/pypi/feedparser/>`_
* `JQuery 1.8.1 <http://jquery.com/>`_
* `JQuery UI 1.10.2 <http://jqueryui.com/>`_

.. index:: Usage

Usage
-----

.. _image-annotated-output:
.. image:: _static/annotated_output.png
    :alt: annotated feedreader output

In the image above:

1. Menu controlling what output is displayed.

2. Most recent entries/stories.

3. Toggle between showing all entries or only those which are unread.

4. Show entries from all feeds.
   In brackets is number of unread entries.
   Clicking on this number marks them all as read.

5. Accordion of feed groups.
   As well as the group name each button shows the number of unread
   entries.

6. Feed group. Shows the feed names.
   These can be individually selected.
   The down-arrows can be clicked to poll an individual feed
   or all those in the group.

7. Feeds not in any group.

8. String search feed and entry text.

9. Link to Django Admin.

10. Import feeds in OPML xml format.

11. Export feeds in OPML xml format.

In addition to explicitly marking sets of entries as read,
scrolling to the end of the page causes all of the unread entries
displayed to that point to be marked as read.
Additional entries, if any exist, are added to list displayed.

Django Admin can be used to add or remove feeds from the
`Feed <code.html#feedreader.models.Feed>`_ model.
Adding a new feed causes it to be polled immediately.

The numbers of entries initially displayed, how many entries are saved
in the local database and how many additionally entries are displayed
on scrolling tot he bottom of the page are set in the
`Options <code.html#feedreader.models.Options>`_ model.
