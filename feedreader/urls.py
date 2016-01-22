from __future__ import absolute_import

from django.conf.urls import url

from .views import (FeedList, Search, EntryList,
                    NumbersUnread, MarkEntryRead,
                    EditFeeds, ExportOpml, UpdateItem)

urlpatterns = [
   url(regex=r'^$',
       view=FeedList.as_view(),
       name='feed_list'),
   url(regex=r'^entry_list/$',
       view=EntryList.as_view(),
       name='entry_list'),
   url(regex=r'^num_unread/$',
       view=NumbersUnread.as_view(),
       name='num_unread'),
   url(regex=r'^mark_entry_read/$',
       view=MarkEntryRead.as_view(),
       name='mark_entry_read'),
   url(regex=r'^search/$',
       view=Search.as_view(),
       name='search'),
   url(regex=r'^edit_feeds/$',
       view=EditFeeds.as_view(),
       name='edit_feeds'),
   url(regex=r'^export_opml/$',
       view=ExportOpml.as_view(),
       name='export_opml'),
   url(regex=r'^update/$',
       view=UpdateItem.as_view(),
       name='update_item'),
]
