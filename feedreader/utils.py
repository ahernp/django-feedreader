from datetime import datetime
from time import mktime

import feedparser
import pytz

from django.conf import settings
from django.utils import html
from django.utils import timezone
from django.utils.translation import ugettext as _

from .models import Entry, Options, Group, Feed

import logging

logger = logging.getLogger('feedreader')


def build_context(request, context={}):
    """
    Find flag and id values in the request and use them
    to build a common context dictionary. Including the
    list of entries to display.
    """
    options = Options.manager.get_options()
    poll_flag = request.GET.get('poll_flag', None)
    mark_read_flag = request.GET.get('mark_read_flag', None)
    show_read_flag = request.GET.get('show_read_flag', None)

    last_entry = None
    last_entry_id = request.GET.get('entry_id', None)  # Last entry on page
    if last_entry_id:
        try:
            last_entry = Entry.objects.get(pk=last_entry_id)
        except Entry.DoesNotExist:
            pass

    context['show_read_flag'] = show_read_flag
    feed = None
    feed_id = request.GET.get('feed_id', None)
    if feed_id:
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            pass

    group = None
    group_id = request.GET.get('group_id', None)
    if group_id:
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            pass

    if feed:
        if mark_read_flag:
            entries = Entry.objects.filter(feed=feed, read_flag=False)
            entries.update(read_flag=True)
        if poll_flag:
            poll_feed(feed)
        if show_read_flag:
            entries = Entry.objects.filter(feed=feed)
        else:
            entries = Entry.objects.filter(feed=feed, read_flag=False)
        context['entries_header'] = feed.title
    elif group:
        feeds = Feed.objects.filter(group=group)
        if mark_read_flag:
            entries = Entry.objects.filter(feed__group=group, read_flag=False)
            entries.update(read_flag=True)
        if poll_flag:
            for feed in feeds:
                poll_feed(feed)
        if show_read_flag:
            entries = Entry.objects.filter(feed__group=group)
        else:
            entries = Entry.objects.filter(feed__group=group, read_flag=False)
        context['entries_header'] = group.name
    else:
        if mark_read_flag:
            entries = Entry.objects.filter(read_flag=False)
            entries.update(read_flag=True)
        if show_read_flag:
            entries = Entry.objects.all()
        else:
            entries = Entry.objects.filter(read_flag=False)
        context['entries_header'] = _('All Entries')

    if last_entry:
        entry_list = list(entries)
        if last_entry in entry_list:
            last_entry_pos = entry_list.index(last_entry)
            for i in range(last_entry_pos + 1):
                if entry_list[i].read_flag == False:
                    entry_list[i].read_flag = True
                    entry_list[i].save()
            del entry_list[:last_entry_pos + 1]
            context['entry_list'] = entry_list[:options.number_additionally_displayed]
        else:
            context['entry_list'] = []
        context['entries_header'] = None
    else:
        context['entry_list'] = entries[:options.number_initially_displayed]

    return context


def poll_feed(db_feed, verbose=False):
    """
    Read through a feed looking for new entries.
    """
    options = Options.manager.get_options()
    parsed = feedparser.parse(db_feed.xml_url)
    if hasattr(parsed.feed, 'bozo_exception'):
        # Malformed feed
        msg = 'Feedreader poll_feeds found Malformed feed, "%s": %s' % (db_feed.xml_url, parsed.feed.bozo_exception)
        logger.warning(msg)
        if verbose:
            print(msg)
        return
    if hasattr(parsed.feed, 'published_parsed'):
        if parsed.feed.published_parsed is None:
            published_time = timezone.now()
        else:
            published_time = datetime.fromtimestamp(mktime(parsed.feed.published_parsed))
        try:
            published_time = pytz.timezone(settings.TIME_ZONE).localize(published_time, is_dst=None)
        except pytz.exceptions.AmbiguousTimeError:
            pytz_timezone = pytz.timezone(settings.TIME_ZONE)
            published_time = pytz_timezone.localize(published_time, is_dst=False)
        if db_feed.published_time and db_feed.published_time >= published_time:
            return
        db_feed.published_time = published_time
    for attr in ['title', 'title_detail', 'link']:
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
    if hasattr(parsed.feed, 'description_detail') and hasattr(parsed.feed, 'description'):
        if parsed.feed.description_detail.type == 'text/plain':
            db_feed.description = html.escape(parsed.feed.description)
        else:
            db_feed.description = parsed.feed.description
    else:
        db_feed.description = ''
    db_feed.last_polled_time = timezone.now()
    db_feed.save()
    if verbose:
        print('%d entries to process in %s' % (len(parsed.entries), db_feed.title))
    for i, entry in enumerate(parsed.entries):
        if i >= options.max_entries_saved:
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
            if verbose:
                print(msg)
            logger.warning(msg)
            continue
        db_entry, created = Entry.objects.get_or_create(feed=db_feed, link=entry.link)
        if created:
            if hasattr(entry, 'published_parsed'):
                if entry.published_parsed is None:
                    published_time = timezone.now()
                else:
                    published_time = datetime.fromtimestamp(mktime(entry.published_parsed))
                    try:
                        published_time = pytz.timezone(settings.TIME_ZONE).localize(published_time, is_dst=None)
                    except pytz.exceptions.AmbiguousTimeError:
                        pytz_timezone = pytz.timezone(settings.TIME_ZONE)
                        published_time = pytz_timezone.localize(published_time, is_dst=False)
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
