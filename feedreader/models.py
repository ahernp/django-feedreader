from django.db import models


class OptionsManager(models.Manager):
    def get_options(self):
        options = Options.objects.all()
        if options:
            options = options[0]
        else:  # Create options row with default values
            options = Options.objects.create()
        return options


class Options(models.Model):
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
    number_initially_displayed = models.IntegerField(default=10)
    number_additionally_displayed = models.IntegerField(default=5)
    max_entries_saved = models.IntegerField(default=100)

    objects = models.Manager()
    manager = OptionsManager()

    class Meta:
        verbose_name_plural = "options"

    def __str__(self):
        return u'Options'


class Group(models.Model):
    """
    Group of feeds.

    :Fields:

        name : char
            Name of group.
    """
    name = models.CharField(max_length=250, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def num_unread_entries(self):
        return Entry.objects.filter(feed__group=self, read_flag=False).count()


class Feed(models.Model):
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
        updated_time : date_time
            When feed was last updated.
        last_polled_time : date_time
            When feed was last polled.
        group : ForeignKey
            Group this feed is a part of.
    """
    title = models.CharField(max_length=2000, blank=True, null=True)
    xml_url = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=2000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    published_time = models.DateTimeField(blank=True, null=True)
    last_polled_time = models.DateTimeField(blank=True, null=True)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title or self.xml_url

    def num_unread_entries(self):
        return Entry.objects.filter(feed=self, read_flag=False).count()


    def save(self, *args, **kwargs):
        """Poll new Feed"""
        try:
            Feed.objects.get(xml_url=self.xml_url)
            super(Feed, self).save(*args, **kwargs)
        except Feed.DoesNotExist:
            super(Feed, self).save(*args, **kwargs)
            from feedreader.utils import poll_feed

            poll_feed(self)


class EntryManager(models.Manager):
    def num_unread(self):
        return Entry.objects.filter(read_flag=False).count()


class Entry(models.Model):
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
        updated_time : date_time
            When entry was last updated.
    """
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=2000, blank=True, null=True)
    link = models.CharField(max_length=2000)
    description = models.TextField(blank=True, null=True)
    published_time = models.DateTimeField(auto_now_add=True)
    read_flag = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_time']
        verbose_name_plural = 'entries'

    def __str__(self):
        return self.title

    objects = models.Manager()
    manager = EntryManager()
