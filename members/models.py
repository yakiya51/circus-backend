from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

ROLE_CHOICES = (
    ('Main Tank', u'Main Tank'),
    ('Off Tank', u'Off Tank'),
    ('Main DPS', u'Main DPS'),
    ('Flex DPS', u'Flex DPS'),
    ('Main Support', u'Main Support'),
    ('Flex Support', u'Flex Support')
)


class EntranceKey(models.Model):
    code = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.code


class Member(AbstractUser):
#    ip_address = models.GenericIPAddressField(blank=True, null=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES,
                            blank=False, null=False, default='Change me')
    battle_tag = models.CharField(max_length=24, blank=False, null=False)
    twitter = models.CharField(max_length=50, blank=True, null=True)
    discord = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.battle_tag is not None:
            return self.battle_tag
        elif len(self.battle_tag) <= 0:
            return f'{self.id} No battletag set.'
        else:
            return f'{self.id} No battletag set.'

    def natural_key(self):
        return self.battle_tag


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
