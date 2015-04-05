"""Feedreader Models Unit Test."""
from __future__ import absolute_import

from django.test import TestCase

from .models import Entry, Feed, Group, Options
from .simple_test_server import (PORT, setUpModule as server_setup,
                                 tearDownModule as server_teardown)


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class OptionsTest(TestCase):
    """
    Create and access Options.
    """

    def setUp(self):
        self.options = Options.manager.get_options()

    def test_options_unicode(self):
        """Retrieve Options object's unicode string."""
        options_unicode = self.options.__unicode__()
        self.assertEqual(options_unicode,
                         'Options',
                         'Options: Unexpected __unicode__ value: Got %s expected "Options"' %
                         (options_unicode))


class GroupTest(TestCase):
    """
    Create and access Group.
    """

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')

    def test_group_unicode(self):
        """Retrieve Group object's unicode string."""
        group_unicode = self.group.__unicode__()
        self.assertEqual(group_unicode,
                         'Test Group',
                         'Group: Unexpected __unicode__ value: Got %s expected "Test Group"' %
                         (group_unicode))


class FeedTest(TestCase):
    """
    Create and access Feed.
    """

    def setUp(self):
        self.feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
        self.feed.title = 'Test Feed'
        self.feed.save()

    def test_feed_unicode(self):
        """Retrieve Feed object's unicode string."""
        feed_unicode = self.feed.__unicode__()
        self.assertEqual(feed_unicode,
                         'Test Feed',
                         'Feed: Unexpected __unicode__ value: Got %s expected "Test Feed"' %
                         (feed_unicode))


class EntryTest(TestCase):
    """
    Create and access Entry.
    """

    def setUp(self):
        self.feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
        self.entry = Entry.objects.create(feed=self.feed,
                                          title='Test Entry',
                                          link='http://example.com/test')

    def test_entry_unicode(self):
        """Retrieve Entry object's unicode string."""
        entry_unicode = self.entry.__unicode__()
        self.assertEqual(entry_unicode,
                         'Test Entry',
                         'Entry: Unexpected __unicode__ value: Got %s expected "Test Entry"' %
                         (entry_unicode))
