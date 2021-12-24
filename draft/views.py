from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser


from matchqueue.models import Queue
from members.models import Member
from draft.serializers import DraftSerializer
from draft.models import Draft

from permissions import IsAdminOrReadOnly

from random import randint, shuffle


class DraftViewSet(viewsets.ModelViewSet):
    queryset = Draft.objects.all()
    serializer_class = DraftSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @ action(detail=True, methods=['GET', 'POST'])
    def update_draft(self, request, pk=None):
        """
        Updates a draft instance in the database.
        Request must include:
            - Which team is drafting
            - Who was drafted
        """
        try: 
            draft = Draft.objects.get(pk=pk) 
        except Draft.DoesNotExist: 
            return Response({'message': 'The draft does not exist'}, status=status.HTTP_404_NOT_FOUND) 
        # Parse request data 
        draft_data = request.data
        
        # Add drafted player to whichever team they were drafted by
        # I should probably check if current user is actually a team captain?
        if draft_data['team_drafting'] == 'blue':
            draft.blue_team.add(draft_data['player_drafted'])
        else:
            draft.red_team.add(draft_data['player_drafted'])
        
        # Remove drafted player from player pool
        draft.player_pool.remove(draft_data['player_drafted'])
        draft.save()
        return Response(data={'updated': True})
