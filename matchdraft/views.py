from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from matchdraft.serializers import MatchDraftSerializer
from matchdraft.models import MatchDraft

from permissions import IsAdminOrReadOnly

from random import shuffle


def create_draft(match_players, captains):
    # match players =  all players in the match 
    # player pool   =  only draftable players
    blue_captain = captains['blue']
    red_captain = captains['red']
    player_pool = match_players

    # Remove both captains from player pool
    for player in captains.values():
        player_pool.remove(player)
    
    # Randomly choose which captain gets first pick
    shuffled_captains = captains.values().shuffle()
    # Create draft object
    MatchDraft.objects.create(
        captain_drafting=shuffled_captains[1],
        blue_captain=blue_captain,
        red_captain=red_captain,
        blue_team=[blue_captain], 
        red_team=[red_captain],
        player_pool=player_pool 
    )


class MatchDraftViewSet(viewsets.ModelViewSet):
    queryset = MatchDraft.objects.all()
    serializer_class = MatchDraftSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @ action(detail=True, methods=['POST'])
    def update_draft(self, request, pk=None):
        """
        Updates a draft instance in the database.
        """
        try: 
            draft = MatchDraft.objects.get(pk=pk) 
        except MatchDraft.DoesNotExist: 
            return Response({'message': 'The draft does not exist'}, status=status.HTTP_404_NOT_FOUND) 

        data = request.data
        serializer = MatchDraftSerializer(instance=draft, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'updated': True})
        else:
            return Response({'message': 'Failed to update draft.'}) 
