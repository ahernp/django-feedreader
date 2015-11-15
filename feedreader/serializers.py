from __future__ import absolute_import
from rest_framework import serializers

from .models import Entry, Feed, Group, Options


class OptionsSerializer(serializers.ModelSerializer):
    """
    Options controlling feedreader behavior

    :Fields:

        number_initially_displayed : integer
            Number of entries, from all feeds, initially displayed on webpage.
        number_additionally_displayed : integer
            Number of entries added to displayed results when scrolling down.
        max_entries_saved : integer
            Maximum number of entries to store for each feed.
    """

    class Meta:
        model = Options


class GroupSerializer(serializers.ModelSerializer):
    """
    Group of feeds.

    :Fields:

        name : char
            Name of group.
        num_unread_entries: int
    """

    class Meta:
        model = Group


class FeedSerializer(serializers.ModelSerializer):
    """
    Feed information.

    :Fields:

        title : char
            Title of feed.
        xml_url : char
            URL of xml feed.
        link : char
            URL of feed site.
        description : text
            Description of feed.
        published_time : date_time
            When feed was last updated.
        last_polled_time : date_time
            When feed was last polled.
        group : ForeignKey
            Group this feed is a part of.
        num_unread_entries
    """

    class Meta:
        model = Feed


class EntrySerializer(serializers.ModelSerializer):
    """
    Feed entry information.

    :Fields:

        feed : ForeignKey
            Feed this entry is a part of.
        title : char
            Title of entry.
        link : char
            URL of entry.
        description : text
            Description of entry.
        published_time : date_time
            When entry was last updated.
        read_flag: boolean
            Has the entry been read?
    """

    class Meta:
        model = Entry

