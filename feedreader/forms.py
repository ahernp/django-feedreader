from __future__ import absolute_import

from xml.etree import ElementTree

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

    def clean_opml_file(self):
        """Check OPML file contents."""
        opml_file = data = self.cleaned_data['opml_file']
        try:
            opml_tree = ElementTree.parse(opml_file)
        except ElementTree.ParseError as e:
            raise forms.ValidationError('Error Parsing OPML file: %s' % e.msg)
        return opml_tree