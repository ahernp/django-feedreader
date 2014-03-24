from __future__ import absolute_import

import json

from xml.etree import ElementTree
from xml.dom import minidom

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.views.generic import ListView, TemplateView, View

from braces.views import LoginRequiredMixin

from .forms import StringSearchForm, ImportOpmlFileForm
from .models import Options, Group, Feed, Entry
from .utils import poll_feed, build_context


class NumbersUnread(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """Count numbers of unread entries, return in json object"""
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


class EntryList(LoginRequiredMixin, ListView):
    """List of Entries"""
    model = Entry
    template_name = 'feedreader/entry_list.html'
    extra_context = {}

    def dispatch(self, request, *args, **kwargs):
        self.extra_context = build_context(request)
        self.queryset = self.extra_context['entry_list']
        return super(EntryList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EntryList, self).get_context_data(**kwargs)
        self.extra_context.update(context)
        return self.extra_context


class MarkEntryRead(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
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


class FeedList(LoginRequiredMixin, ListView):
    """List of Feeds by Group and those in no Group"""
    model = Group
    template_name = 'feedreader/feed_list.html'
    extra_context = {}

    def dispatch(self, request, *args, **kwargs):
        self.extra_context = build_context(request)
        return super(FeedList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FeedList, self).get_context_data(**kwargs)
        context['no_group'] = Feed.objects.filter(group=None)
        context['import_form'] = ImportOpmlFileForm()
        self.extra_context.update(context)
        return self.extra_context


class Search(LoginRequiredMixin, TemplateView):
    """
    Simple string search.

    Display entries with titles and/or descriptions which 
    contain the string searched for.
    """
    template_name = 'feedreader/search_results.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = StringSearchForm(request.GET)
        search_string = form.cleaned_data['feedreader_search_string'] if form.is_valid() else ''
        context['feedreader_search_string'] = search_string
        if len(search_string) < 3:
            context['too_small'] = True
        else:
            title_matches = Entry.objects.filter(title__icontains=search_string)
            description_matches = Entry.objects.filter(description__icontains=search_string)
            context['title_matches'] = title_matches
            context['description_matches'] = description_matches
        return self.render_to_response(context)


class ImportOpml(LoginRequiredMixin, View):
    """
    Import feed subscriptions in OPML format
    """
    def post(self, request, *args, **kwargs):
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


class ExportOpml(LoginRequiredMixin, View):
    """
    Return feed subscriptions in OPML format.
    """
    def get(self, request, *args, **kwargs):
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
