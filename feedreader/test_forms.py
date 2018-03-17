"""Feedreader Forms Unit Test."""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import AddFeedsForm

INVALID_OPML = b"""<?xml version="1.0" ?>
<opml version="2.0">
  <head>
    <title>Feedreader Feeds</title>
  </head>
  <body>
    <outline text="ahernp.com blog" type="rss" xmlUrl="http://ahernp.com/blog/feed"/>
    <outline text="News">
      <outline text="Reuters: Most Read Articles" type="rss" xmlUrl="http://feeds.reuters.com/reuters/MostRead?format=xml"/>

  </body>
</opml>
"""


class AddFeedsFormTest(TestCase):
    """
    Test AddFeedsForm feeds.
    """

    def setUp(self):
        self.opml_file = SimpleUploadedFile("feedreader.opml", INVALID_OPML)

    def test_invalid_opml(self):
        """Test Group already on database"""
        form = AddFeedsForm({}, {'opml_file': self.opml_file})
        self.assertEqual(form.is_valid(),
                         False,
                         'Expected invalid AddFeedsForm')
        self.assertEqual('opml_file' in form.errors,
                         True,
                         'Expected error on "opml_file" in AddFeedsForm')
        self.assertEqual(form.errors['opml_file'][0],
                         'Error Parsing OPML file: mismatched tag: line 11, column 4',
                         'Expected "Error Parsing OPML file: mismatched tag: line 11, column 4" error in AddFeedsForm')
