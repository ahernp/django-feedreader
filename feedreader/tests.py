"""Feedreader Unit Test."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from .factories import GroupFactory, FeedFactory, EntryFactory
from .models import Options
from .simple_test_server import (PORT, setUpModule as server_setup,
                                 tearDownModule as server_teardown)

from mock import patch

TEST_URLS = [
    # (url, status_code, text_on_page)
    ('/feedreader/', 200, 'Feed Reader'),
    ('/feedreader/num_unread', 200, 'unread_feed'),
    # Poll Feed
    ('/feedreader/entry_list?feed_id=1&poll_flag=1', 200, '<div id="entry_id='),
    # Poll Group
    ('/feedreader/entry_list?group_id=1&poll_flag=1', 200, None),
    # Last entry_id included
    ('/feedreader/entry_list?feed_id=1&entry_id=1', 200, '<div id="entry_id='),
    # Non-existant Group and Feed
    ('/feedreader/entry_list?group_id=99&feed_id=99&entry_id=99', 200, '<div id="entry_id='),
    # Mark group as Read
    ('/feedreader/entry_list?group_id=1&mark_read_flag=1', 200, None),
    # Mark feed as Read
    ('/feedreader/entry_list?feed_id=1&mark_read_flag=1', 200, None),
    # Mark all as Read
    ('/feedreader/entry_list?mark_read_flag=1', 200, None),
    # Mark entry as Read
    ('/feedreader/mark_entry_read?entry_id=1', 200, None),
    # Feed show read
    ('/feedreader/entry_list?feed_id=1&show_read_flag=1', 200, None),
    # Group show read
    ('/feedreader/entry_list?group_id=1&show_read_flag=1', 200, None),
    # Show all read
    ('/feedreader/entry_list?show_read_flag=1', 200, None),
    # Entry not found
    ('/feedreader/entry_list?feed_id=1&entry_id=1', 200, None),
    # No entries found in Group
    ('/feedreader/entry_list?group_id=1', 200, '<p id="no_entries">'),
    # No entries found in Feed
    ('/feedreader/entry_list?feed_id=1', 200, '<p id="no_entries">'),
    # Search
    ('/feedreader/search?feedreader_search_string=co-op', 200, 'Search Results for'),
    # Search string too small
    ('/feedreader/search?feedreader_search_string=py', 200, 'Search string too small: "py".'),
    # Export feeds in OPML format
    ('/feedreader/export_opml', 200, 'feed')
]


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class WorkingURLsTest(TestCase):
    """
    Visit various URLs in Feedreader to ensure they are working.
    """

    def setUp(self):
        """Create data and login"""
        entry = EntryFactory.create()
        group = GroupFactory.create()
        feed = FeedFactory.create()
        feed.xml_url = 'http://localhost:%s/test/feed' % PORT
        feed.group = group
        feed.save()

        self.user = get_user_model().objects.create_user('john', 'john@montypython.com', 'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

    def test_urls(self):
        """Visit each URL in turn"""
        for url, status_code, expected_text in TEST_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code,
                             status_code,
                             'URL %s: Unexpected status code, got %s expected %s' %
                             (url, response.status_code, status_code))
            if response.status_code == 200 and expected_text:
                self.assertContains(response,
                                    expected_text,
                                    msg_prefix='URL %s' % (url))


class TestPollFeedsCommand(TestCase):
    """
    Test the command which polls the feeds.
    """

    def setUp(self):
        """Create data"""
        entry = EntryFactory.create()
        group = GroupFactory.create()
        feed = FeedFactory.create()
        feed.xml_url = 'http://localhost:%s/test/feed' % PORT
        feed.group = group
        feed.save()

    def test_poll_feeds(self):
        """Test poll_feeds command."""
        args = []
        opts = {'verbose': True}

        # Ensure some Entries are deleted
        feedreader_options = Options.manager.get_options()
        feedreader_options.max_entries_saved = 1
        feedreader_options.save()
        with patch('sys.stdout', new=StringIO()):  # Suppress printed output from test
            call_command('poll_feeds', *args, **opts)

        # Default Options created if none are found
        Options.objects.all().delete()
        with patch('sys.stdout', new=StringIO()):  # Suppress printed output from test
            call_command('poll_feeds', *args, **opts)
