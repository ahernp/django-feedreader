"""
This command polls all of the Feeds and removes old entries.
"""
from django.core.management.base import BaseCommand

from ...constants import MAX_ENTRIES_SAVED
from ...models import Feed, Entry
from ...utils import poll_feed

import logging

logger = logging.getLogger('feedreader')


class Command(BaseCommand):
    help = 'Polls all Feeds for Entries.'

    def add_arguments(self, parser):
        """
        Add named (optional) argument
        """
        parser.add_argument('--verbose',
                            action='store_true',
                            dest='verbose',
                            default=False,
                            help='Print progress on command line')

    def handle(self, *args, **options):
        """
        Read through all the feeds looking for new entries.
        """
        verbose = options['verbose']
        feeds = Feed.objects.all()
        num_feeds = len(feeds)

        if verbose:
            print('%d feeds to process' % (num_feeds))

        for i, feed in enumerate(feeds):
            if verbose:
                print('(%d/%d) Processing Feed %s' % (i + 1, num_feeds, feed.title))

            poll_feed(feed, verbose)

            # Remove older entries
            entries = Entry.objects.filter(feed=feed)[MAX_ENTRIES_SAVED:]

            for entry in entries:
                entry.delete()

            if verbose:
                print('Deleted %d entries from feed %s' % ((len(entries), feed.title)))

        logger.info('Feedreader poll_feeds completed successfully')
