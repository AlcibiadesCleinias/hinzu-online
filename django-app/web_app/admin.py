from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.urls import reverse

from cryptography.fernet import Fernet

# Register your models here.
from .models import Embed, Rate


class EmbedAdmin(admin.ModelAdmin):
    list_display = ('id', 'path2similar', 'embeds_of_original')


class RateAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Embeds',           {'fields': ['embeds']}),
        ('Additional info',             {'fields': ['image_tag', 'rate', 'path2combined', 'pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('embeds', 'rate', 'image_tag','was_published_recently', 'path2combined', 'pub_date')
    list_filter = ['pub_date']

    def image_tag(self, obj):
        path2image = obj.path2combined
        f = Fernet(settings.FERNET_KEY)
        path2image = f.encrypt(path2image.encode())
        return format_html('<a href={url} target="_blank"><img src="{url}" width="108" height="192" /></a>'.format(url=reverse('web_app:fetchImage', args=(path2image.decode(),))))

    image_tag.short_description = 'Image'
    readonly_fields = ['image_tag']


admin.site.register(Embed, EmbedAdmin)
admin.site.register(Rate, RateAdmin)
