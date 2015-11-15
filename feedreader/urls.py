from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, url, include

from .views import (FeedList, Search, EntryList,
                    NumbersUnread, MarkEntryRead,
                    EditFeeds, ExportOpml, UpdateItem)

urlpatterns = patterns('',
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
)

if 'rest_framework' in settings.INSTALLED_APPS:
    print('Loading REST extensions for django-feedreader')
    from rest_framework.routers import DefaultRouter
    from .api import EntryViewSet, FeedViewSet, GroupViewSet, OptionsViewSet


    # Create a router and register our ViewSets with it.
    router = DefaultRouter()
    router.register(r'options', OptionsViewSet)
    router.register(r'group', GroupViewSet)
    router.register(r'feed', FeedViewSet)
    router.register(r'entry', EntryViewSet)

    # The API URLs are now determined automatically by the router.
    # Additionally, we include the login URLs for the browsable API.
    urlpatterns += [
        url(r'^api/', include(router.urls)),
    ]
