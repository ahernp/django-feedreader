from __future__ import absolute_import

import json

from xml.etree import ElementTree
from xml.dom import minidom

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from .forms import StringSearchForm, ImportOpmlFileForm
from .models import Options, Group, Feed, Entry
from .utils import poll_feed


def build_context(get):
    """Build common context dictionary""" 
    context = {}
    poll_flag = get.get('poll_flag', None)
    mark_read_flag = get.get('mark_read_flag', None)
    show_read_flag = get.get('show_read_flag', None)

    last_entry = None
    last_entry_id = get.get('entry_id', None)  # Last entry on page
    if last_entry_id:
        try:
            last_entry = Entry.objects.get(pk=last_entry_id)
        except Entry.DoesNotExist:
            pass
    context['show_read_flag'] = show_read_flag
    feed = None
    feed_id = get.get('feed_id', None)
    if feed_id:
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            pass
    group = None
    group_id = get.get('group_id', None)
    if group_id:
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            pass

    options = Options.objects.all()
    if options:
        options = options[0]
    else:  # Create options row with default values
        options = Options.objects.create()
    if feed:
        if mark_read_flag:
            entries = Entry.objects.filter(feed=feed, read_flag=False)
            entries.update(read_flag=True)
        if poll_flag:
            poll_feed(feed)
        if show_read_flag:
            entries = Entry.objects.filter(feed=feed)
        else:
            entries = Entry.objects.filter(feed=feed, read_flag=False)
        context['entries_header'] = feed.title
    elif group:
        feeds = Feed.objects.filter(group=group)
        if mark_read_flag:
            entries = Entry.objects.filter(feed__group=group, read_flag=False)
            entries.update(read_flag=True)
        if poll_flag:
            for feed in feeds:
                poll_feed(feed)
        if show_read_flag:
            entries = Entry.objects.filter(feed__group=group)
        else:
            entries = Entry.objects.filter(feed__group=group, read_flag=False)
        context['entries_header'] = group.name
    else:
        if mark_read_flag:
            entries = Entry.objects.filter(read_flag=False)
            entries.update(read_flag=True)
        if show_read_flag:
            entries = Entry.objects.all()
        else:
            entries = Entry.objects.filter(read_flag=False)
        context['entries_header'] = 'All items'
    if last_entry:
        entries = list(entries)
        if last_entry in entries:
            last_entry_pos = entries.index(last_entry)
            for i in range(last_entry_pos + 1):
                if entries[i].read_flag == False:
                    entries[i].read_flag = True
                    entries[i].save()
            del entries[:last_entry_pos + 1]
            context['entries'] = entries[:options.number_additionally_displayed]
        else:
            context['entries'] = []
        context['entries_header'] = None
    else:
        context['entries'] = entries[:options.number_initially_displayed]
    return context


@login_required
def ajax_get_num_unread(request):
    """Count numbers of unread entries"""
    context = {}
    context['unread_total'] = Entry.objects.filter(read_flag=False).count()
    groups = Group.objects.all()
    for group in groups:
        num_unread = Entry.objects.filter(feed__group=group, read_flag=False).count()
        context['unread_group%s' % (group.id)] = num_unread
        context['unread_group_button%s' % (group.id)] = num_unread
    feeds = Feed.objects.all()
    for feed in feeds:
        context['unread_feed%s' % (feed.id)] = Entry.objects.filter(feed=feed, read_flag=False).count()
    return HttpResponse(json.dumps(context), content_type='application/json')


@login_required
def ajax_get_feeds(request):
    """Get feed contents"""
    context = build_context(request.GET)
    return render_to_response('feedreader/feed_entries.html', context, RequestContext(request))


@login_required
def ajax_mark_entry_read(request):
    """Mark entry as read"""
    entry_id = request.GET.get('entry_id', None)
    if entry_id:
        try:
            entry = Entry.objects.get(pk=entry_id)
            if entry.read_flag == False:
                entry.read_flag = True
                entry.save()
        except Entry.DoesNotExist:
            pass
    return HttpResponse('')


@login_required
def feeds(request):
    """Show most recent feed contents on page"""
    context = build_context(request.GET)
    context['groups'] = Group.objects.all()
    context['no_group'] = Feed.objects.filter(group=None)
    context['import_form'] = ImportOpmlFileForm()
    return render_to_response('feedreader/feeds.html', context, RequestContext(request))


def search_entries(request):
    """
    Simple string search.

    Display entries with titles and/or descriptions which contain the string searched for.
    """
    form = StringSearchForm(request.GET)
    search_string = form.cleaned_data['feedreader_search_string'] if form.is_valid() else ''
    if len(search_string) < 3:
        return render_to_response('feedreader/search_results.html',
                                  {'feedreader_search_string': search_string, 'too_small': True},
                                  RequestContext(request))
    title_matches = Entry.objects.filter(title__icontains=search_string)
    description_matches = Entry.objects.filter(description__icontains=search_string)
    context = {'title_matches': title_matches,
               'description_matches': description_matches,
               'feedreader_search_string': search_string,
              }
    return render_to_response('feedreader/search_results.html', context, RequestContext(request))


def import_opml(request):
    """
    Import feed subscriptions in OPML format
    """
    form = ImportOpmlFileForm(request.POST, request.FILES)
    if form.is_valid():
        tree = ElementTree.parse(request.FILES['opml_file'])
        group = None
        for node in tree.iter('outline'):
            name = node.attrib.get('text')
            url = node.attrib.get('xmlUrl')
            if name and url:
                try:
                    feed = Feed.objects.get(xml_url=url)
                except Feed.DoesNotExist:
                    Feed.objects.create(xml_url=url, group=group)
            else:
                group, created = Group.objects.get_or_create(name=name)
    return redirect(reverse('admin:feedreader_feed_changelist'))


def export_opml(request):
    """Return feed subscriptions in OPML format."""
    root = ElementTree.Element('opml')
    root.set('version', '2.0')
    head = ElementTree.SubElement(root, 'head')
    title = ElementTree.SubElement(head, 'title')
    title.text = 'Feedreader Feeds'
    body = ElementTree.SubElement(root, 'body')

    feeds = Feed.objects.filter(group=None)
    for feed in feeds:
        feed_xml = ElementTree.SubElement(body,
                              'outline',
                              {'type': 'rss',
                               'text': feed.title,
                               'xmlUrl': feed.xml_url,
                               }
        )

    groups = Group.objects.all()
    for group in groups:
        group_xml = ElementTree.SubElement(body,
                               'outline',
                               {'text': group.name,
                                }
        )
        feeds = Feed.objects.filter(group=group)
        for feed in feeds:
            feed_xml = ElementTree.SubElement(group_xml,
                                  'outline',
                                  {'type': 'rss',
                                   'text': feed.title,
                                   'xmlUrl': feed.xml_url,
                                   }
            )
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="feedreader.opml"'
    response.write(minidom.parseString(ElementTree.tostring(root, 'utf-8')).toprettyxml(indent="  "))
    return response
