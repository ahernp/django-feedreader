"""Feedreader Forms Unit Test."""
from __future__ import absolute_import

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import AddFeedsForm

from mock import Mock, patch

INVALID_OPML = """<?xml version="1.0" ?>
<opml version="2.0">
  <head>
    <title>Feedreader Feeds</title>
  </head>
  <body>
    <outline text="ahernp.com blog" type="rss" xmlUrl="http://ahernp.com/blog/feed"/>
    <outline text="News">
      <outline text="Reuters: Most Read Articles" type="rss" xmlUrl="http://feeds.reuters.com/reuters/MostRead?format=xml"/>

  </body>
</opml>
"""


class AddFeedsFormTest(TestCase):
    """
    Test AddFeedsForm feeds.
    """

    def setUp(self):
        # Create Feed and Group mock objects
        self.feed_mock = Mock()
        self.group_mock = Mock()
        self.opml_file = SimpleUploadedFile("feedreader.opml", INVALID_OPML)

    def test_duplicate_feed(self):
        """Test Feed already on database"""
        with patch('feedreader.forms.Feed', self.feed_mock):
            form = AddFeedsForm({'feed_url': 'wibble'})
            self.assertEqual(form.is_valid(),
                             False,
                             'Expected invalid AddFeedsForm')
            self.assertEqual('feed_url' in form.errors,
                             True,
                             'Expected error on "feed_url" in AddFeedsForm')
            self.assertEqual(form.errors['feed_url'][0],
                             'Feed already exists',
                             'Expected "Feed already exists" error in AddFeedsForm')


    def test_duplicate_group(self):
        """Test Group already on database"""
        with patch('feedreader.forms.Group', self.group_mock):
            form = AddFeedsForm({'new_group': 'wibble'})
            self.assertEqual(form.is_valid(),
                             False,
                             'Expected invalid AddFeedsForm')
            self.assertEqual('new_group' in form.errors,
                             True,
                             'Expected error on "new_group" in AddFeedsForm')
            self.assertEqual(form.errors['new_group'][0],
                             'Group already exists',
                             'Expected "Group already exists" error in AddFeedsForm')

    def test_invalid_opml(self):
        """Test Group already on database"""
        form = AddFeedsForm({}, {'opml_file': self.opml_file})
        self.assertEqual(form.is_valid(),
                         False,
                         'Expected invalid AddFeedsForm')
        self.assertEqual('opml_file' in form.errors,
                         True,
                         'Expected error on "opml_file" in AddFeedsForm')
        self.assertEqual(form.errors['opml_file'][0],
                         'Error Parsing OPML file: mismatched tag: line 11, column 4',
                         'Expected "Error Parsing OPML file: mismatched tag: line 11, column 4" error in AddFeedsForm')
