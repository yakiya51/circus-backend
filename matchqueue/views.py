from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from matches.models import Match

from matchqueue.models import Queue
from matchqueue.serializers import QueueSerializer
from members.models import Member

from permissions import IsAdminOrReadOnly


class RoleInQueue:
    def __init__(self, role):
        self.role = role
        self.players_queued = []
        self.is_enough = False
    
    def append_player_battle_tag(self, player):
        self.players_queued.append(player.battle_tag)


class InQueue:
    def __init__(self):
        self.main_tank      =   RoleInQueue('Main Tank')
        self.off_tank       =   RoleInQueue('Off Tank')
        self.main_dps       =   RoleInQueue('Main DPS')
        self.flex_dps       =   RoleInQueue('Flex DPS')
        self.main_support   =   RoleInQueue('Main Support')
        self.flex_support   =   RoleInQueue('Flex Support')
    

    def add_player(self, player):
        # Refactor player role (string) to match class attribute name.
        attr_name = player.role.lower().replace(' ', '_')
        # Get role attribute
        role_queue_attribute = getattr(self, attr_name)
        # Append player's battle tag to the queue in the player's role.
        role_queue_attribute.append_player_batte_tag(player)


    def role_is_filled(self, role):
        attr_name = role.lower().replace(' ', '_')
        role_queue_attr = getattr(self, attr_name)
        if role_queue_attr:
            pass


def walk_players(players):
    # Setup dict with lists for each role..
    in_queue = {
        'Main Tank':
        {
            'players_queued': [],
            'is_enough': False
        },
        'Off Tank':
        {
            'players_queued': [],
            'is_enough': False
        },
        'Main DPS': 
        {
            'players_queued': [],
            'is_enough': False
        },
        'Flex DPS':
        {
            'players_queued': [],
            'is_enough': False
        },
        'Main Support':
        {
            'players_queued': [],
            'is_enough': False
        },
        'Flex Support': 
        {
            'players_queued': [],
            'is_enough': False
        }
    }

    # Iterate over all players in queue..
    for player in players.all():
        if player.role == 'Change me':
            continue

        if in_queue[player.role]['is_enough']:
            print(f'{player.role} has enough players to form a match.')
        in_queue[player.role]['players_queued'].append(player.battle_tag)

    # Check if there are at least 2 players in queue for each role..
    fillable_rolls = 0
    for key in in_queue.keys():
        # Switch is_enough for the current role if two or more players in queue are of that role.
        if not in_queue[key]['is_enough'] and len(in_queue[key]['players_queued']) >= 2:
            in_queue[key]['is_enough'] = True
        
        if in_queue[key]['is_enough']:
            fillable_rolls += 1
    
    if fillable_rolls == 6:
        blue_team = []
        red_team = []

        # Slotting roles
        # Main tank
        blue_team.append(in_queue['Main Tank']['players_queued'][0])
        red_team.append(in_queue['Main Tank']['players_queued'][1])
        # Off tank
        blue_team.append(in_queue['Off Tank']['players_queued'][0])
        red_team.append(in_queue['Off Tank']['players_queued'][1])
        # Main DPS
        blue_team.append(in_queue['Main DPS']['players_queued'][0])
        red_team.append(in_queue['Main DPS']['players_queued'][1])
        # Flex DPS
        blue_team.append(in_queue['Flex DPS']['players_queued'][0])
        red_team.append(in_queue['Flex DPS']['players_queued'][1])
        # Main Support 
        blue_team.append(in_queue['Main Support']['players_queued'][0])
        red_team.append(in_queue['Main Support']['players_queued'][1])
        # Flex Support 
        blue_team.append(in_queue['Flex Support']['players_queued'][0])
        red_team.append(in_queue['Flex Support']['players_queued'][1])

        print('Blue team players\n--------------------')
        for p in blue_team:
            print(p.username)

        print('Red team players\n--------------------')
        for p in red_team:
            print(p.username)
        
        match = Match.objects.create(
            blue_captain=blue_team[0], red_captain=red_team[0], map='Busan')
        
        match.blue_team.set(blue_team)
        match.red_team.set(red_team)
        match.save()

        # Remove assigned players from the queue.
        queue = Queue.objects.get(id=1)
        for player in blue_team:
            queue.players.remove(player)

        for player in red_team:
            queue.players.remove(player)

        # Send create match packet to match server with id match.id
        print(f'Not impemented: Send packet to match server with id of {match.id}')



class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @ action(detail=True, methods=['POST'])
    def join_queue(self, request, pk=None):
        queue = Queue.objects.get(id=pk)
        # This is fucking retarded
        # request.user *should* be looking at the Authorization header to auto authenticate.
        # but it's not. war crime.
        instance = Token.objects.get(key=request.headers.get(
            'Authorization').split('Token ')[1])
        queue.players.add(Member.objects.get(id=instance.user_id))

        walk_players(queue.players)

        return HttpResponse('Added')

    @ action(detail=True, methods=['POST'])
    def leave_queue(self, request, pk=None):
        if pk is not None:
            queue = Queue.objects.get(id=pk)
            instance = Token.objects.get(key=request.headers.get(
                'Authorization').split('Token ')[1])
            queue.players.remove(Member.objects.get(id=instance.user_id))
            return Response(data={'removed': True})
        return HttpResponse('<h1>tf u doin</h1>')


    @ action(detail=True, methods=['GET'])
    def contains(self, request, pk=None):
        in_queue = None

        if pk is not None:
            instance = Token.objects.get(key=request.headers.get(
                'Authorization').split('Token ')[1])
            if Member.objects.get(id=instance.user_id) in Queue.objects.get(id=pk).players.all():
                in_queue = True
            else:
                in_queue = False

        return Response(data={'in_queue': in_queue})
