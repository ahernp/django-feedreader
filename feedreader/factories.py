"""Factories used to create data for testing."""
from .models import Group, Feed, Entry
from .simple_test_server import PORT

import factory


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group
        abstract = False

    name = factory.Sequence(lambda n: 'Test Group {0}'.format(n))


class FeedFactory(factory.DjangoModelFactory):
    class Meta:
        model = Feed
        abstract = False

    xml_url = factory.Sequence(lambda n: 'http://localhost:{0}/test{1}/feed'.format(PORT, n))


class EntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Entry
        abstract = False

    feed = factory.SubFactory(FeedFactory)
    title = factory.Sequence(lambda n: 'Test Entry {0}'.format(n))
    link = 'http://example.com/test/feed'
    description = '%s\n\nDescription' % title
