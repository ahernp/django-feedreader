"""Feedreader Utils Unit Test."""
from __future__ import absolute_import

from StringIO import StringIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import Client

from .models import Entry

from mock import Mock, patch

OPML = """<?xml version="1.0" ?>
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
            url = '/feedreader/mark_entry_read/?entry_id=1'
            response = self.client.get(url)
            self.assertEqual(response.status_code,
                             200,
                             'URL %s: Unexpected status code, got %s expected 200' %
                             (url, response.status_code))

    def test_mark_missing_entry(self):
        """Mark unread entry as read"""
        entry_get_mock = Mock()
        entry_get_mock.side_effect = Entry.DoesNotExist
        with patch('feedreader.views.Entry.objects.get', entry_get_mock):
            url = '/feedreader/mark_entry_read/?entry_id=1'
            response = self.client.get(url)
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
        url = '/feedreader/import_opml/'
        response = self.client.post(url, {'opml_file': self.opml_file})
        self.assertEqual(response.status_code,
                         302,
                         'URL %s: Unexpected status code, got %s expected 302' %
                            (url, response.status_code))
