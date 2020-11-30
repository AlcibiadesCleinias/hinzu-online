import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Embed(models.Model):
    path2similar = models.CharField(max_length=200)
    embeds_of_original = models.BinaryField()


class Rate(models.Model):
    embeds = models.ForeignKey(Embed, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(blank=True, null=True)
    path2combined = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def __str__(self):
        return self.path2combined.split('/')[-1]
