from __future__ import absolute_import

from django.urls import path

from .views import (FeedList, Search, EntryList,
                    NumbersUnread, MarkEntryRead,
                    EditFeeds, ExportOpml, UpdateItem)

app_name = 'feedreader'
urlpatterns = [
   path('', view=FeedList.as_view(), name='feed_list'),
   path('entry_list', view=EntryList.as_view(), name='entry_list'),
   path('num_unread', view=NumbersUnread.as_view(), name='num_unread'),
   path('mark_entry_read', view=MarkEntryRead.as_view(), name='mark_entry_read'),
   path('search', view=Search.as_view(), name='search'),
   path('edit_feeds', view=EditFeeds.as_view(), name='edit_feeds'),
   path('export_opml', view=ExportOpml.as_view(), name='export_opml'),
   path('update', view=UpdateItem.as_view(), name='update_item'),
]
