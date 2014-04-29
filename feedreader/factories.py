"""Factories used to create data for testing."""
from __future__ import absolute_import

from .models import Group, Feed, Entry
from .simple_test_server import PORT

import factory


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group

    name = factory.Sequence(lambda n: 'Test Group {0}'.format(n))


class FeedFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Feed

    xml_url = factory.Sequence(lambda n: 'http://localhost:{0}/test{1}/feed'.format(PORT, n))


class EntryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Entry

    feed = factory.SubFactory(FeedFactory)
    title = factory.Sequence(lambda n: 'Test Entry {0}'.format(n))
    link = 'http://example.com/test/feed'
    description = '%s\n\nDescription' % title
