"""Feedreader Unit Test."""

from django.core.management import call_command
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from .models import Options

TEST_URLS = [
    # (url, status_code, text_on_page)
    ('/feedreader/', 200, 'Feed Reader'),
    ('/feedreader/entry_list/?feed_id=1&poll_flag=1', 200, '<div id="entry_id=1"'),
    ('/feedreader/num_unread/', 200, 'unread_feed'),
    ('/feedreader/entry_list/?eed_id=1&entry_id=1', 200, '<div id="entry_id='),
]


class WorkingURLsTest(TestCase):
    """
    Visit various URLs in Feedreader to ensure they are working.
    """
    fixtures = ['dmcm/fixtures/unit_test.json']
    def test_urls(self):
        """Visit each URL in turn"""
        self.user = get_user_model().objects.create_user('john', 'john@montypython.com', 'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')
        for url, status_code, expected_text in TEST_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code,
                             status_code,
                             'URL %s: Unexpected status code, got %s expected %s' %
                                (url, response.status_code, status_code))
            if response.status_code == 200:
                self.assertContains(response,
                                    expected_text,
                                    msg_prefix='URL %s' % (url))


class TestBranchImport(TestCase):
    """
    Test the command which polls the feeds.
    """
    def test_poll_feeds(self):
        """Test poll_feeds command."""
        args = []
        opts = {'verbose': True}

        # Ensure some Entries are deleted
        feedreader_options = Options.objects.all()[0]
        feedreader_options.max_entries_saved = 1
        feedreader_options.save()
        call_command('poll_feeds', *args, **opts)

        # Command creates default Options if none are found
        Options.objects.all().delete()
        call_command('poll_feeds', *args, **opts)
