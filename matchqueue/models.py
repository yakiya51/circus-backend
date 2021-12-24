from django.db import models
from members.models import Member


class Queue(models.Model):
    players = models.ManyToManyField(Member, blank=True)
    queue_type = models.CharField(default="Standard", max_length=32)

    def __str__(self):
        return self.queue_type
