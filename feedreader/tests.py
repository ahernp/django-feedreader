"""Feedreader Unit Test."""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User


TEST_URLS = [
    # (url, status_code, text_on_page)
    ('/feedreader/', 200, 'Feed Reader'),
]


class WorkingURLsTest(TestCase):
    """
    Visit various URLs in Feedreader to ensure they are working.
    """
    fixtures = ['dmcm/fixtures/unit_test.json']
    def test_urls(self):
        """Visit each URL in turn"""
        self.user = User.objects.create_user('john', 'john@montypython.com', 'password')
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

