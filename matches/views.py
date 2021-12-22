from itertools import chain

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from matches.models import Match
from matches.serializers import MatchSerializer

from permissions import IsAdminOrReadOnly


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(detail=False, methods=['GET'])
    def sort(self, request):
        queryset = None

        if 'username' in request.query_params:
            red = Match.objects.filter(red_team__username=request.query_params.get('username'))
            blue = Match.objects.filter(blue_team__username=request.query_params.get('username'))
            queryset = list(chain(red, blue))

        return Response(MatchSerializer(instance=queryset, many=True).data)

    @action(detail=False, methods=['GET'])
    def motd(self, request):
        f = open('motd.txt', 'r')
        return HttpResponse(f.read(), content_type='text/plain')
