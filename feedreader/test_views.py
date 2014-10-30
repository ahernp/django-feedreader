"""Feedreader Utils Unit Test. Designed for py.test"""
from __future__ import absolute_import

from StringIO import StringIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import Client

from .factories import GroupFactory, FeedFactory, EntryFactory
from .forms import AddFeedsForm
from .models import Entry, Feed, Group
from .simple_test_server import (PORT, setUpModule as server_setup,
                                 tearDownModule as server_teardown)
from .views import EditFeeds, UpdateItem

from mock import Mock, patch

import pytest

OPML = """<?xml version="1.0" ?>
<opml version="2.0">
  <head>
    <title>Feedreader Feeds</title>
  </head>
  <body>
    <outline text="ahernp.com blog" type="rss" xmlUrl="https://ahernp.com/blog/feed"/>
    <outline text="News">
      <outline text="ahernp.com blog" type="rss" xmlUrl="https://ahernp.com/blog/feed"/>
    </outline>
  </body>
</opml>
"""

def test_mark_unread_entry(admin_client):
    """Mark unread entry as read"""
    entry = EntryFactory.create()
    entry.read_flag = False
    entry.save()

    url = '/feedreader/mark_entry_read/?entry_id=%s' % (entry.id)
    response = admin_client.get(url, secure=True)
    assert response.status_code == 200

def test_mark_missing_entry(admin_client):
    """Mark unread entry as read"""
    entry_get_mock = Mock()
    entry_get_mock.side_effect = Entry.DoesNotExist
    with patch('feedreader.views.Entry.objects.get', entry_get_mock):
        url = '/feedreader/mark_entry_read/?entry_id=1'
        response = admin_client.get(url, secure=True)
        assert response.status_code == 200

def test_loading_opml_file(admin_client):
    """Load OPML file"""
    opml_file = SimpleUploadedFile("feedreader.opml", OPML)
    url = '/feedreader/edit_feeds/'
    response = admin_client.post(url,
                                 {'opml_file': opml_file},
                                 secure=True)
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_new_feed():
    """Create new feed and group"""
    def dict_lookup(*args):
        returns = {'feed_url': 'test_url',
                   'feed_group': 'test_group',
                   'new_group': 'test_new_group',
                   'opml_file': None}
        return returns[args[0]]
    form_mock = Mock()
    form_mock.cleaned_data.get.side_effect = dict_lookup
    feed_class_mock = Mock(spec=Feed)
    request_mock = Mock()

    with patch('feedreader.views.AddFeedsForm', form_mock):
        with patch('feedreader.views.Feed', feed_class_mock):
            edit_feeds_view = EditFeeds()
            edit_feeds_view.request = request_mock
            response = edit_feeds_view.form_valid(form_mock)
            assert response.status_code == 200

def setUpModule():
    server_setup()

def tearDownModule():
    server_teardown()

@pytest.fixture(scope='module')
def group_on_db(db):
    """Populate Database"""
    group = Group.objects.create(name='Test Group')
    return group

@pytest.fixture(scope='module')
def feed_on_db(db, group_on_db):
    """Populate Database"""
    feed = Feed.objects.create(xml_url='http://localhost:%s/test/feed' % (PORT))
    feed.group = group_on_db
    feed.save()
    return feed

def test_delete_item(admin_client, feed_on_db):
    """Delete item"""
    url = '/feedreader/update/'
    response = admin_client.post(url,
                                 {'identifier': 'feedreader-Feed-delete-%s' % feed_on_db.id,
                                     'data_value': 'on'},
                                 secure=True)
    assert response.status_code == 200

def test_update_text(admin_client, feed_on_db):
    """Update text field"""
    url = '/feedreader/update/'
    response = admin_client.post(url,
                                 {'identifier': 'feedreader-Feed-title-%s' % feed_on_db.id,
                                     'data_value': 'Test Title 2'},
                                 secure=True)
    assert response.status_code == 200

    feed = Feed.objects.get(pk=feed_on_db.id)
    assert feed.title == 'Test Title 2'

def test_update_boolean(admin_client, admin_user):
    """Update boolean field"""
    url = '/feedreader/update/'
    response = admin_client.post(url,
                                 {'identifier': 'auth-User-is_superuser-%s' % admin_user.id,
                                  'data_value': 'true'},
                                 secure=True)
    assert response.status_code == 200

def test_update_foreignkey(admin_client, feed_on_db, group_on_db):
    """Update foreign key"""
    url = '/feedreader/update/'
    response = admin_client.post(url,
                                 {'identifier': 'feedreader-Feed-group-%s' % feed_on_db.id,
                                      'data_value': group_on_db.id},
                                 secure=True)
    assert response.status_code == 200

    # Update foreign key to None
    response = admin_client.post(url,
                                 {'identifier': 'feedreader-Feed-group-%s' % feed_on_db.id,
                                      'data_value': ''},
                                 secure=True)
    assert response.status_code == 200
