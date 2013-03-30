import feedparser
from datetime import datetime
from time import mktime
from feedreader.models import Entry, Options

import logging
logger = logging.getLogger('feedreader')

def poll_feed(db_feed, verbose=False):
    """
    Read through a feed looking for new entries.
    """
    options = Options.objects.all()[0]
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
        if db_feed.published_time and db_feed.published_time >= published_time:
            return
        db_feed.published_time = published_time
    for attr in ['title', 'link', 'description']:
        if not hasattr(parsed.feed, attr):
            msg = 'Feedreader poll_feeds. Feed "%s" has no %s' % (db_feed.xml_url, attr)
            logger.error(msg)
            if verbose:
                print(msg)
            return
    db_feed.title = parsed.feed.title
    db_feed.link = parsed.feed.link
    db_feed.description = parsed.feed.description
    db_feed.last_polled_time = datetime.now()
    db_feed.save()
    if verbose:
        print('%d entries to process in %s' % (len(parsed.entries), db_feed.title))
    for i, entry in enumerate(parsed.entries):
        if i > options.max_entries_saved:
            break
        for attr in ['title', 'link', 'description']:
            if not hasattr(entry, attr):
                msg = 'Feedreader poll_feeds. Entry "%s" has no %s' % (entry.link, attr)
                logger.error(msg)
                if verbose:
                    print(msg)
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
                now = datetime.now()
                if published_time > now:
                    published_time = now
                db_entry.published_time = published_time
            db_entry.title = entry.title
            db_entry.description = entry.description
            db_entry.save()
