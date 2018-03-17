"""Feedreader Models Unit Test."""
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

    def test_options_str(self):
        """Retrieve Options object's str string."""
        options_str = self.options.__str__()
        self.assertEqual(options_str,
                         'Options',
                         'Options: Unexpected __str__ value: Got %s expected "Options"' %
                         (options_str))


class GroupTest(TestCase):
    """
    Create and access Group.
    """

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')

    def test_group_str(self):
        """Retrieve Group object's str string."""
        group_str = self.group.__str__()
        self.assertEqual(group_str,
                         'Test Group',
                         'Group: Unexpected __str__ value: Got %s expected "Test Group"' %
                         (group_str))


class FeedTest(TestCase):
    """
    Create and access Feed.
    """

    def setUp(self):
        self.feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
        self.feed.title = 'Test Feed'
        self.feed.save()

    def test_feed_str(self):
        """Retrieve Feed object's str string."""
        feed_str = self.feed.__str__()
        self.assertEqual(feed_str,
                         'Test Feed',
                         'Feed: Unexpected __str__ value: Got %s expected "Test Feed"' %
                         (feed_str))


class EntryTest(TestCase):
    """
    Create and access Entry.
    """

    def setUp(self):
        self.feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
        self.entry = Entry.objects.create(feed=self.feed,
                                          title='Test Entry',
                                          link='http://example.com/test')

    def test_entry_str(self):
        """Retrieve Entry object's str string."""
        entry_str = self.entry.__str__()
        self.assertEqual(entry_str,
                         'Test Entry',
                         'Entry: Unexpected __str__ value: Got %s expected "Test Entry"' %
                         (entry_str))
