from __future__ import absolute_import

from datetime import datetime
from time import mktime

import feedparser
import pytz

from django.conf import settings
from django.utils import html
from django.utils import timezone

from .models import Entry, Options, Group, Feed

import logging
logger = logging.getLogger('feedreader')

def poll_feed(db_feed, verbose=False):
    """
    Read through a feed looking for new entries.
    """
    options = Options.objects.all()
    if options:
        options = options[0]
    else:  # Create options row with default values
        options = Options.objects.create()
    parsed = feedparser.parse(db_feed.xml_url)
    if hasattr(parsed.feed, 'bozo_exception'):
        # Malformed feed
        msg = 'Feedreader poll_feeds found Malformed feed, %s: %s' % (db_feed.xml_url, parsed.feed.bozo_exception)
        logger.warning(msg)
        if verbose:
            print(msg)
        return
    if hasattr(parsed.feed, 'published_parsed'):
        published_time = datetime.fromtimestamp(mktime(parsed.feed.published_parsed))
        published_time = pytz.timezone(settings.TIME_ZONE).localize(published_time, is_dst=None)
        if db_feed.published_time and db_feed.published_time >= published_time:
            return
        db_feed.published_time = published_time
    for attr in ['title', 'title_detail', 'link', 'description', 'description_detail']:
        if not hasattr(parsed.feed, attr):
            msg = 'Feedreader poll_feeds. Feed "%s" has no %s' % (db_feed.xml_url, attr)
            logger.error(msg)
            if verbose:
                print(msg)
            return
    if parsed.feed.title_detail.type == 'text/plain':
        db_feed.title = html.escape(parsed.feed.title)
    else:
        db_feed.title = parsed.feed.title
    db_feed.link = parsed.feed.link
    if parsed.feed.description_detail.type == 'text/plain':
        db_feed.description = html.escape(parsed.feed.description)
    else:
        db_feed.description = parsed.feed.description
    db_feed.last_polled_time = timezone.now()
    db_feed.save()
    if verbose:
        print('%d entries to process in %s' % (len(parsed.entries), db_feed.title))
    for i, entry in enumerate(parsed.entries):
        if i > options.max_entries_saved:
            break
        missing_attr = False
        for attr in ['title', 'title_detail', 'link', 'description']:
            if not hasattr(entry, attr):
                msg = 'Feedreader poll_feeds. Entry "%s" has no %s' % (entry.link, attr)
                logger.error(msg)
                if verbose:
                    print(msg)
                missing_attr = True
        if missing_attr:
            continue
        if entry.title == "":
            msg = 'Feedreader poll_feeds. Entry "%s" has a blank title' % (entry.link)
            logger.warning(msg)
            if verbose:
                print(msg)
            continue
        db_entry, created = Entry.objects.get_or_create(feed=db_feed, link=entry.link)
        if created:
            if hasattr(entry, 'published_parsed'):
                published_time = datetime.fromtimestamp(mktime(entry.published_parsed))
                published_time = pytz.timezone(settings.TIME_ZONE).localize(published_time, is_dst=None)
                now = timezone.now()
                if published_time > now:
                    published_time = now
                db_entry.published_time = published_time
            if entry.title_detail.type == 'text/plain':
                db_entry.title = html.escape(entry.title)
            else:
                db_entry.title = entry.title
            # Lots of entries are missing descrtion_detail attributes. Escape their content by default
            if hasattr(entry, 'description_detail') and entry.description_detail.type != 'text/plain':
                db_entry.description = entry.description
            else:
                db_entry.description = html.escape(entry.description)
            db_entry.save()
