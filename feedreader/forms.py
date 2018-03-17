from xml.etree import ElementTree

from django import forms

from feedreader.models import Feed, Group


class StringSearchForm(forms.Form):
    """
    Allow user to enter a string to search the for matching entries.
    """
    feedreader_search_string = forms.CharField()


class AddFeedsForm(forms.Form):
    """
    Add feeds individually or using an OPML file.
    """
    feed_url = forms.CharField(required=False)
    feed_group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    new_group = forms.CharField(required=False)
    opml_file = forms.FileField(required=False)

    def clean_feed_url(self):
        """Check new feed url not on database."""
        feed_url = self.cleaned_data['feed_url']
        try:
            Feed.objects.get(xml_url=feed_url)
            raise forms.ValidationError('Feed already exists')
        except Feed.DoesNotExist as e:
            pass
        return feed_url

    def clean_new_group(self):
        """Check new Group not on database."""
        new_group = self.cleaned_data['new_group']
        try:
            Group.objects.get(name=new_group)
            raise forms.ValidationError('Group already exists')
        except Group.DoesNotExist as e:
            pass
        return new_group

    def clean_opml_file(self):
        """Check OPML file contents."""
        opml_file = self.cleaned_data['opml_file']
        if opml_file:
            try:
                opml_tree = ElementTree.parse(opml_file)
            except ElementTree.ParseError as e:
                raise forms.ValidationError('Error Parsing OPML file: %s' % e.msg)
            return opml_tree