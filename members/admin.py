from django.contrib import admin

from members.models import Member, EntranceKey

admin.site.register(Member)
admin.site.register(EntranceKey)