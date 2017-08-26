from django.conf import settings

MAX_ENTRIES_SAVED = getattr(settings, 'MAX_ENTRIES_SAVED', 100)

LOGOUT_URL = getattr(settings, 'LOGOUT_URL', '/accounts/logout/')
