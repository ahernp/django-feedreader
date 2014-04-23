"""Feedreader Utils Unit Test."""
from __future__ import absolute_import

from datetime import datetime
from StringIO import StringIO

from django.test import TestCase

from .models import Feed
from .utils import poll_feed

from mock import Mock, patch
import pytz


@patch('feedreader.utils.feedparser.parse')
class TestPollFeed(TestCase):
    """
    Test polling feeds.
    """
    def setUp(self):
        feed_mock = Mock(spec=Feed)
        feed_mock.xml_url = 'test-feed-url'
        feed_mock.published_time = None
        self.feed_mock = feed_mock

    def test_bozo_exception(self, parse_mock):
        """Test with Bozo Exception returned"""
        parse_mock.return_value.feed.bozo_exception = 'bozo_exception returned'
        with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
            poll_feed(self.feed_mock, verbose=True)

    def test_published_time(self, parse_mock):
        """Test Published Time variations"""
        del parse_mock.return_value.feed.bozo_exception
        parse_mock.return_value.feed.published_parsed = (2014, 01, 01,
                                                         12, 0, 0,
                                                         2, 1, 0)  # 2014-01-01 12:00:00

        # No published time in DB
        feed_mock = self.feed_mock
        feed_mock.published_time = None
        with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
            poll_feed(feed_mock, verbose=True)

        # Published time in DB later than on feed
        feed_mock.published_time = pytz.utc.localize(datetime(2014, 01, 01, 13, 0, 0))
        with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
            poll_feed(feed_mock, verbose=True)

    def test_missing_attribute(self, parse_mock):
        """Test with missing attribute: description_detail"""
        del parse_mock.return_value.feed.bozo_exception
        parse_mock.return_value.feed.published_parsed = (2014, 01, 01,
                                                         12, 0, 0,
                                                         2, 1, 0)  # 2014-01-01 12:00:00
        del parse_mock.return_value.feed.description_detail
        with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
            poll_feed(self.feed_mock, verbose=True)

    def test_with_feed_description(self, parse_mock):
        """Test with missing attribute: description_detail"""
        del parse_mock.return_value.feed.bozo_exception
        parse_mock.return_value.feed.published_parsed = (2014, 01, 01,
                                                         12, 0, 0,
                                                         2, 1, 0)  # 2014-01-01 12:00:00
        parse_mock.return_value.feed.description_detail.type = 'text/plain'
        parse_mock.return_value.feed.description = 'Test Feed Description'
        with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
            poll_feed(self.feed_mock, verbose=True)


@patch('feedreader.utils.feedparser.parse')
class TestPollEntries(TestCase):
    def setUp(self):
        feed_mock = Mock(spec=Feed)
        feed_mock.xml_url = 'test-feed-url'
        feed_mock.published_time = None
        self.feed_mock = feed_mock

    def test_feed_entry_blank_title(self, parse_mock):
        """Test with missing attribute: description_detail"""
        del parse_mock.return_value.feed.bozo_exception
        parse_mock.return_value.feed.published_parsed = (2014, 01, 01,
                                                         12, 0, 0,
                                                         2, 1, 0)  # 2014-01-01 12:00:00
        entry_attrs = {'link': 'test_entry_link',
                       'published_parsed': (2014, 01, 01, 12, 0, 0, 2, 1, 0),  # 2014-01-01 12:00:00
                       }
        entry_mock = Mock(**entry_attrs)
        entry_mock.title = ''
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch('feedreader.utils.Entry', db_entry_mock):
            # with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_missing_description(self, parse_mock):
        """Test with missing attribute: description_detail"""
        del parse_mock.return_value.feed.bozo_exception
        parse_mock.return_value.feed.published_parsed = (2014, 01, 01,
                                                         12, 0, 0,
                                                         2, 1, 0)  # 2014-01-01 12:00:00
        entry_attrs = {'link': 'test_entry_link',
                       'published_parsed': (2014, 01, 01, 12, 0, 0, 2, 1, 0),  # 2014-01-01 12:00:00
                       }
        entry_mock = Mock(**entry_attrs)
        del entry_mock.description
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch('feedreader.utils.Entry', db_entry_mock):
            # with patch('sys.stdout', new=StringIO()) as fake_out:  # Suppress printed output from test
                poll_feed(self.feed_mock, verbose=True)

