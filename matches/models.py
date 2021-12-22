from django.db import models

from members.models import Member

MAP_CHOICES = (
    ('King\'s Row', u'King\'s Row'),
    ('Numbani', u'Numbani'),
    ('Blizzard World', u'Blizzard World'),
    ('Hollywood', u'Hollywood'),
    ('Lijiang Tower', u'Lijiang Tower'),
    ('Illios', u'Illios'),
    ('Oasis', u'Oasis'),
    ('Busan', u'Busan'),
    ('Nepal', u'Nepal'),
    ('Route 66', u'Route 66'),
    ('Havana', u'Havana'),
    ('Rialto', u'Rialto'),
    ('Watchpoint: Gibraltar', u'Watchpoint: Gibraltar'),
    ('Junkertown', u'Junkertown'),
    ('Dorado', u'Dorado'),
)
STATE_CHOICES = (
    ('drafting', u'drafting'),
    ('map_vote', u'map_vote'),
    ('playing', u'playing'),
    ('completed', u'completed')
)
WIN_CHOICES = (('blue', u'blue'), ('red', u'red'))


class Match(models.Model):
    blue_team = models.ManyToManyField(Member, related_name='blueteam')
    red_team = models.ManyToManyField(Member, related_name='redteam')
    blue_captain = models.ForeignKey(Member, related_name='bluecaptain', on_delete=models.CASCADE)
    red_captain = models.ForeignKey(Member, related_name='redcaptain', on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)
    map = models.CharField(max_length=40, choices=MAP_CHOICES, null=True, blank=True)
    outcome = models.CharField(max_length=5, choices=WIN_CHOICES, null=True, blank=True)
    state = models.CharField(max_length=15, choices=STATE_CHOICES, null=False, blank=False, default='drafting')

    def __str__(self):
        return f'{self.map} Blue({self.blue_captain.username}) Red({self.red_captain.username})'
