from django.conf.urls import patterns, url
from feedreader.views import (feeds, search_entries, ajax_get_feeds,
                              ajax_get_num_unread, ajax_mark_entry_read,
                              import_opml, export_opml)

urlpatterns = patterns(
    '',
    url(r'^$', feeds),
    url(r'^get_feeds/$', ajax_get_feeds),
    url(r'^get_num_unread/$', ajax_get_num_unread),
    url(r'^mark_entry_read/$', ajax_mark_entry_read),
    url(r'^search_entries/$', search_entries, name='feedreader_search_entries'),
    url(r'^import_opml/$', import_opml, name='feedreader_import_opml'),
    url(r'^export_opml/$', export_opml, name='feedreader_export_opml'),
)
