from rest_framework import viewsets

from .models import Entry, Feed, Group, Options
from .serializers import EntrySerializer, FeedSerializer, GroupSerializer, OptionsSerializer


class OptionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Options.objects.all()
    serializer_class = OptionsSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FeedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer