from django.contrib import admin

from .models import Options, Group, Feed, Entry


class OptionsAdmin(admin.ModelAdmin):
    list_display = ['number_initially_displayed', 'number_additionally_displayed', 'max_entries_saved']


admin.site.register(Options, OptionsAdmin)


class GroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Group, GroupAdmin)


class FeedAdmin(admin.ModelAdmin):
    list_display = ['xml_url', 'title', 'group', 'published_time', 'last_polled_time']
    list_filter = ['group']
    search_fields = ['link', 'title']
    readonly_fields = ['title', 'link', 'description', 'published_time',
                       'last_polled_time']
    fieldsets = (
        (None, {
            'fields': (('xml_url', 'group',),
                       ('title', 'link',),
                       ('description',),
                       ('published_time', 'last_polled_time',),
            )
        }),
    )


admin.site.register(Feed, FeedAdmin)


class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'feed', 'published_time']
    list_filter = ['feed']
    search_fields = ['title', 'link']
    readonly_fields = ['link', 'title', 'description', 'published_time', 'feed']
    fieldsets = (
        (None, {
            'fields': (('link',),
                       ('title', 'feed',),
                       ('description',),
                       ('published_time', 'read_flag'),
            )
        }),
    )


admin.site.register(Entry, EntryAdmin)
