from django.db import models
from members.models import Member


class MatchDraft(models.Model):
    captain_drafting    =   models.ForeignKey(Member, related_name='captain_drafting', on_delete=models.CASCADE)
    blue_captain        =   models.ForeignKey(Member, related_name='bluecaptain_draft', on_delete=models.CASCADE)
    red_captain         =   models.ForeignKey(Member, related_name='redcaptain_draft', on_delete=models.CASCADE)
    blue_team           =   models.ManyToManyField(Member, related_name='blueteam_draft', blank=True)
    red_team            =   models.ManyToManyField(Member, related_name='redteam_draft', blank=True)
    player_pool         =   models.ManyToManyField(Member, related_name='playerpool', blank=True)

    def __str__(self):
        return f'currently drafting: {self.captain_drafting}'
