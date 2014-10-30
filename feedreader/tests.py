"""Feedreader Unit Test. Designed for py.test"""
from __future__ import absolute_import

import SimpleHTTPServer
from StringIO import StringIO
import SocketServer
import threading

from django.core.management import call_command

from .factories import GroupFactory, FeedFactory, EntryFactory
from .models import Options
from .simple_test_server import (PORT, setUpModule as server_setup,
                                 tearDownModule as server_teardown)

import pytest

TEST_URLS = [
    # (url, status_code, text_on_page)
    ('/feedreader/', 200, 'Feed Reader'),
    ('/feedreader/num_unread/', 200, '"unread_total": 5'),
    # Poll Feed
    ('/feedreader/entry_list/?feed_id=1&poll_flag=1', 200, '<div id="entry_id='),
    # Poll Group
    ('/feedreader/entry_list/?group_id=1&poll_flag=1', 200, None),
    # Last entry_id included
    ('/feedreader/entry_list/?feed_id=1&entry_id=1', 200, '<div id="entry_id='),
    # Non-existant Group and Feed
    ('/feedreader/entry_list/?group_id=99&feed_id=99&entry_id=99', 200, '<div id="entry_id='),
    # Mark group as Read
    ('/feedreader/entry_list/?group_id=1&mark_read_flag=1', 200, None),
    # Mark feed as Read
    ('/feedreader/entry_list/?feed_id=1&mark_read_flag=1', 200, None),
    # Mark all as Read
    ('/feedreader/entry_list/?mark_read_flag=1', 200, None),
    # Mark entry as Read
    ('/feedreader/mark_entry_read/?entry_id=1', 200, None),
    # Feed show read
    ('/feedreader/entry_list/?feed_id=1&show_read_flag=1', 200, None),
    # Group show read
    ('/feedreader/entry_list/?group_id=1&show_read_flag=1', 200, None),
    # Show all read
    ('/feedreader/entry_list/?show_read_flag=1', 200, None),
    # Entry not found
    ('/feedreader/entry_list/?feed_id=1&entry_id=1', 200, None),
    # No entries found in Group
    ('/feedreader/entry_list/?group_id=1', 200, '<p id="no_entries">'),
    # No entries found in Feed
    ('/feedreader/entry_list/?feed_id=1', 200, '<p id="no_entries">'),
    # Search
    ('/feedreader/search/?feedreader_search_string=co-op', 200, 'Search Results for'),
    # Search string too small
    ('/feedreader/search/?feedreader_search_string=py', 200, 'Search string "py" too small.'),
    # Export feeds in OPML format
    ('/feedreader/export_opml/', 200, 'feed')
]

def setUpModule():
    server_setup()

def tearDownModule():
    server_teardown()


def test_urls(admin_client):
    """Visit each URL in turn"""
    entry = EntryFactory.create()
    group = GroupFactory.create()
    feed = FeedFactory.create()
    feed.xml_url = 'http://localhost:%s/test/feed' % PORT
    feed.group = group
    feed.save()

    for url, status_code, expected_text in TEST_URLS:
        response = admin_client.get(url, secure=True)
        assert response.status_code == status_code
        if response.status_code == 200 and expected_text:
            assert expected_text in response.content

@pytest.mark.django_db
def test_poll_feeds():
    """Test poll_feeds command."""
    entry = EntryFactory.create()
    group = GroupFactory.create()
    feed = FeedFactory.create()
    feed.xml_url = 'http://localhost:%s/test/feed' % PORT
    feed.group = group
    feed.save()

    args = []
    opts = {'verbose': True}

    # Ensure some Entries are deleted
    feedreader_options = Options.manager.get_options()
    feedreader_options.max_entries_saved = 1
    feedreader_options.save()
    call_command('poll_feeds', *args, **opts)

    # Default Options created if none are found
    Options.objects.all().delete()
    call_command('poll_feeds', *args, **opts)
