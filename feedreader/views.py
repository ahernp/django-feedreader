from __future__ import absolute_import

import json

from xml.etree import ElementTree
from xml.dom import minidom

from django.apps import apps
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import ListView, FormView, TemplateView, View

from braces.views import LoginRequiredMixin

from .constants import LOGOUT_URL
from .forms import AddFeedsForm, StringSearchForm
from .models import Group, Feed, Entry, Options
from .utils import build_context


class NumbersUnread(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """Count numbers of unread entries, return in json object"""
        context = {'unread_total': Entry.manager.num_unread()}
        groups = Group.objects.all()
        for group in groups:
            num_unread = group.num_unread_entries()
            context['unread_group%s' % (group.id)] = num_unread
            context['unread_group_button%s' % (group.id)] = num_unread
        feeds = Feed.objects.all()
        for feed in feeds:
            context['unread_feed%s' % (feed.id)] = feed.num_unread_entries()
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
        context['logout_url'] = LOGOUT_URL
        context['no_group'] = Feed.objects.filter(group=None)
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
        context['logout_url'] = LOGOUT_URL
        if len(search_string) < 3:
            context['too_small'] = True
        else:
            title_matches = Entry.objects.filter(title__icontains=search_string)
            description_matches = Entry.objects.filter(description__icontains=search_string)
            context['title_matches'] = title_matches
            context['description_matches'] = description_matches
        return self.render_to_response(context)


class EditFeeds(LoginRequiredMixin, FormView):
    """
    Edit feed subscriptions
    """
    template_name = 'feedreader/edit_feeds.html'
    form_class = AddFeedsForm
    success_url = reverse_lazy('feedreader:feed_list')

    def get_context_data(self, **kwargs):
        context = super(EditFeeds, self).get_context_data(**kwargs)
        context['logout_url'] = LOGOUT_URL
        context['groups'] = Group.objects.select_related().all()
        context['no_group'] = Feed.objects.filter(group=None)
        context['feedreader_options'] = Options.manager.get_options()
        return context

    def form_valid(self, form):
        feed_url = form.cleaned_data.get('feed_url')
        feed_group = form.cleaned_data.get('feed_group')
        if feed_url:
            feed = Feed.objects.create(xml_url=feed_url)
            if feed_group:
                feed.group = feed_group
                feed.save()
        new_group = form.cleaned_data.get('new_group')
        if new_group:
            group = Group.objects.create(name=new_group)
        tree = form.cleaned_data.get('opml_file')
        group = None
        if tree:
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
        return self.render_to_response(self.get_context_data(form=form))


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


class UpdateItem(LoginRequiredMixin, View):
    """
    Update value in database.
    @param request: POST includes identifier and new value.

    @return Empty response.
    """

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('identifier', None)
        data_value = request.POST.get('data_value', None)
        if identifier:
            app_label, model_name, fieldname, primary_key = identifier.split('-')
            model = apps.get_model(app_label, model_name)
            if primary_key.isdigit():
                item = model.objects.get(pk=primary_key)
                if fieldname == 'delete':
                    item.delete()
                else:
                    field = model._meta.get_field(fieldname)
                    field_type = field.get_internal_type()
                    if field_type == 'BooleanField':
                        data_value = data_value == 'true'
                    elif field_type == 'ForeignKey':
                        if data_value:
                            data_value = field.remote_field.model.objects.get(pk=data_value)
                            setattr(item, fieldname, data_value)
                        else:
                            setattr(item, fieldname, None)
                    else:
                        setattr(item, fieldname, data_value)
                    item.save()
        return HttpResponse('')
