from itertools import chain

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from matches.models import Match
from matches.serializers import MatchSerializer
from matchqueue.models import Queue
from matchdraft.models import MatchDraft

from permissions import IsAdminOrReadOnly


def create_match(draft_id):
    def print_team_roster(players, team_name):
        print(f'{team_name} Team Players\n--------------------')
        for p in players:
            print(p)
    
    # Get finalized draft
    draft = MatchDraft.objects.filter(id=draft_id)
    # Show roster for both teams
    print_team_roster(draft.blue_team, 'Blue')
    print_team_roster(draft.red_team, 'Red')
    
    # Creat match object
    match = Match.objects.create(
        blue_captain=draft.blue_captain, red_captain=draft.red_captain, map='Busan')
    match.blue_team.set(draft.blue_team)
    match.red_team.set(draft.red_team)
    match.save()

    # Remove assigned players from the queue.
    queue = Queue.objects.get(id=1)
    for player in draft.blue_team:
        queue.players.remove(player)

    for player in draft.red_team:
        queue.players.remove(player)
    
    # Delete the draft
    MatchDraft.objects.filter(id=draft.id).delete()

    # Send create match packet to match server with id match.id
    print(f'Not impemented: Send packet to match server with id of {match.id}')


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @ action(detail=False, methods=['GET'])
    def sort(self, request):
        queryset = None

        if 'username' in request.query_params:
            red = Match.objects.filter(red_team__username=request.query_params.get('username'))
            blue = Match.objects.filter(blue_team__username=request.query_params.get('username'))
            queryset = list(chain(red, blue))

        return Response(MatchSerializer(instance=queryset, many=True).data)

    @ action(detail=False, methods=['GET'])
    def motd(self, request):
        f = open('motd.txt', 'r')
        return HttpResponse(f.read(), content_type='text/plain')
