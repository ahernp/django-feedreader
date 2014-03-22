from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import (feeds, search_entries, ajax_get_feeds,
                    ajax_get_num_unread, ajax_mark_entry_read,
                    import_opml, export_opml)

urlpatterns = patterns('',
    url(regex=r'^$', 
        view=feeds,
        name='feeds'),
    url(regex=r'^get_feeds/$', 
        view=ajax_get_feeds,
        name='get_feeds'),
    url(regex=r'^get_num_unread/$', 
        view=ajax_get_num_unread,
        name='get_num_unreads'),
    url(regex=r'^mark_entry_read/$', 
        view=ajax_mark_entry_read,
        name='mark_entry_read'),
    url(regex=r'^search_entries/$', 
        view=search_entries, 
        name='search_entries'),
    url(regex=r'^import_opml/$', 
        view=import_opml, 
        name='import_opml'),
    url(regex=r'^export_opml/$', 
        view=export_opml, 
        name='export_opml'),
)
