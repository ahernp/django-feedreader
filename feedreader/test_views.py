"""Feedreader Utils Unit Test."""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from .models import Entry, Feed, Group
from .simple_test_server import (PORT, setUpModule as server_setup,
                                 tearDownModule as server_teardown)
from .views import EditFeeds

from mock import Mock, patch

OPML = b"""<?xml version="1.0" ?>
<opml version="2.0">
  <head>
    <title>Feedreader Feeds</title>
  </head>
  <body>
    <outline text="ahernp.com blog" type="rss" xmlUrl="http://ahernp.com/blog/feed"/>
    <outline text="News">
      <outline text="Reuters: Most Read Articles" type="rss" xmlUrl="http://feeds.reuters.com/reuters/MostRead?format=xml"/>
    </outline>
  </body>
</opml>
"""


class MarkEntryReadTest(TestCase):
    """
    Test MarkEntryRead view
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user('john', 'john@montypython.com', 'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

    def test_mark_unread_entry(self):
        """Mark unread entry as read"""
        entry_class_mock = Mock(spec=Entry)
        entry_object_mock = Mock()
        entry_object_mock.read_flag = False
        entry_class_mock.objects.get.return_value = entry_object_mock
        with patch('feedreader.views.Entry', entry_class_mock):
            url = reverse('feedreader:mark_entry_read') + '?entry_id=1'
            response = self.client.get(url, secure=True)
            self.assertEqual(response.status_code,
                             200,
                             'URL %s: Unexpected status code, got %s expected 200' %
                             (url, response.status_code))

    def test_mark_missing_entry(self):
        """Mark unread entry as read"""
        entry_get_mock = Mock()
        entry_get_mock.side_effect = Entry.DoesNotExist
        with patch('feedreader.views.Entry.objects.get', entry_get_mock):
            url = reverse('feedreader:mark_entry_read') + '?entry_id=2'
            response = self.client.get(url, secure=True)
            self.assertEqual(response.status_code,
                             200,
                             'URL %s: Unexpected status code, got %s expected 200' %
                             (url, response.status_code))


class LoadOPMLTest(TestCase):
    """Load OPML file"""

    def setUp(self):
        self.user = get_user_model().objects.create_user('john', 'john@montypython.com', 'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')
        self.opml_file = SimpleUploadedFile("feedreader.opml", OPML)

    def test_loading_opml_file(self):
        """Load OPML file"""
        url = reverse('feedreader:edit_feeds')
        response = self.client.post(url,
                                    {'opml_file': self.opml_file},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'URL %s: Unexpected status code, got %s expected 200' %
                         (url, response.status_code))


class EditFeedsTest(TestCase):
    """
    Test EditFeeds view
    """

    def setUp(self):
        def dict_lookup(*args):
            returns = {'feed_url': 'test_url',
                       'feed_group': 'test_group',
                       'new_group': 'test_new_group',
                       'opml_file': None}
            return returns[args[0]]

        self.form_mock = Mock()
        self.form_mock.cleaned_data.get.side_effect = dict_lookup
        self.feed_class_mock = Mock(spec=Feed)
        self.request_mock = Mock()

    def test_add_new_feed(self):
        """Mark create new feed and group"""
        with patch('feedreader.views.AddFeedsForm', self.form_mock):
            with patch('feedreader.views.Feed', self.feed_class_mock):
                edit_feeds_view = EditFeeds()
                edit_feeds_view.request = self.request_mock
                response = edit_feeds_view.form_valid(self.form_mock)
                self.assertEqual(response.status_code,
                                 200,
                                 'Unexpected status code, got %s expected 200' %
                                 (response.status_code))


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class UpdateItemTest(TestCase):
    """
    Test UpdateItem view
    """

    def setUp(self):
        """Create data and login"""
        self.feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
        self.group = Group.objects.create(name='Test Group')
        self.feed.group = self.group
        self.feed.save()

        self.user = get_user_model().objects.create_user('john',
                                                         'john@montypython.com',
                                                         'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

    def test_delete_item(self):
        """Delete item"""
        url = reverse('feedreader:update_item')
        response = self.client.post(url,
                                    {'identifier': 'feedreader-Feed-delete-%s' % self.feed.id,
                                     'data_value': 'on'},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code, got %s expected 200' %
                         (response.status_code))

    def test_update_text(self):
        """Update text field"""
        url = reverse('feedreader:update_item')
        response = self.client.post(url,
                                    {'identifier': 'feedreader-Feed-title-%s' % self.feed.id,
                                     'data_value': 'Test Title 2'},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code, got %s expected 200' %
                         (response.status_code))
        feed = Feed.objects.get(pk=self.feed.id)
        self.assertEqual(feed.title,
                         'Test Title 2',
                         'Unexpected feed name: Got "%s" expected "Test Title 2"' %
                         (feed.title))


    def test_update_boolean(self):
        """Update boolean field"""
        url = reverse('feedreader:update_item')
        response = self.client.post(url,
                                    {'identifier': 'auth-User-is_superuser-%s' % self.user.id, 'data_value': 'true'},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code, got %s expected 200' %
                         (response.status_code))

    def test_update_foreignkey(self):
        """Update foreign key"""
        url = reverse('feedreader:update_item')
        response = self.client.post(url,
                                    {'identifier': 'feedreader-Feed-group-%s' % self.feed.id,
                                     'data_value': self.group.id},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code, got %s expected 200' %
                         (response.status_code))
        # Update foreign key to None
        response = self.client.post(url,
                                    {'identifier': 'feedreader-Feed-group-%s' % self.feed.id,
                                     'data_value': ''},
                                    secure=True)
        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code, got %s expected 200' %
                         (response.status_code))
