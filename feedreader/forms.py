from __future__ import absolute_import

from django import forms


class StringSearchForm(forms.Form):
    """
    Allow user to enter a string to search the for matching entries.
    """
    feedreader_search_string = forms.CharField()


class ImportOpmlFileForm(forms.Form):
    """
    Load local OPML xml file from browser.
    """
    opml_file = forms.FileField(required=True)
