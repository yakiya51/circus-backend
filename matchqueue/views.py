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
from matchdraft.models import MatchDraft
from matchdraft.views import create_draft

from permissions import IsAdminOrReadOnly

from random import randint, shuffle

ROLES = [   
        'main_tank', 
        'off_tank', 
        'main_support', 
        'flex_support', 
        'main_dps', 
        'flex_dps'
]


class RoleInQueue:
    def __init__(self, role):
        self.role = role
        self.players_queued = None
    
    def add_player_battle_tag(self, player):
        """
        Add a player's battle tag to role in queue.
        """
        if not self.players_queued:
            self.players_queued = [player.battle_tag]
        else:
            self.players_queued.append(player.battle_tag)


class StandardQueue:
    def __init__(self):
        self.main_tank      =   RoleInQueue('Main Tank')
        self.off_tank       =   RoleInQueue('Off Tank')
        self.main_support   =   RoleInQueue('Main Support')
        self.flex_support   =   RoleInQueue('Flex Support')
        self.main_dps       =   RoleInQueue('Main DPS')
        self.flex_dps       =   RoleInQueue('Flex DPS')
    
    def all_roles_filled(self):
        """
        True if there are atleast 2 players queued in all roles.
        False otherwise.
        """ 
        for role_name in ROLES:
            if not self.role_is_filled(role_name):
                return False
        return True
    
    def get_all_players(self):
        """
        Returns a list containing all players in queue.
        """
        players = []
        # Go through each role in the queue
        for role_name in ROLES:
            role_queue_attr = getattr( self, role_name )
            for player in role_queue_attr.players_queued:
                players.append(player)
        return players
    
    def get_match_players(self):
        """
        Returns a list containing the first two battle tags from each role in the queue.
        Will return list of battle tags even if there are not enough players for a match (less than 12)
        """
        players = []
        # Go through each role in the queue
        for role_name in ROLES:
            role_queue_attr = getattr( self, role_name )
            # If there are two or less players queued up for the role, append all players
            if len(role_queue_attr.players_queued) <= 2:
                for player in role_queue_attr.players_queued:
                    players.append(player)
            # Else if there are more than 2 players, append the first two 
            else:
                for i in range(0, 2):
                    players.append(role_queue_attr.players_queued[i])
        return players

    def add_player(self, player):
        """ 
        Add player to their respective role in the queue
        """
        # Refactor player role (string) to match attribute name.
        attr_name = player.role.lower().replace( ' ', '_' )
        # Get role attribute
        role_queue_attribute = getattr( self, attr_name )
        # Append player's battle tag to the queue in the player's role.
        role_queue_attribute.add_player_battle_tag(player)

    def role_is_filled(self, role):
        """
        Returns True if the there are atleast two players queued for the specified role in queue.
        False otherwise.
        """
        # Refactor role string if needed
        if ' ' in role:
            role = role.lower().replace( ' ', '_' )
        role_queue_attr = getattr(self, role)
        # Check if the role has 2 or more players
        if len(role_queue_attr.players_queued) >= 2:
            return True
        else:
            return False


def choose_captains(players):
    """
    Randomly chooses 2 battle tags from a list of 12 as captains and returns a dict.
    """
    if len(players) is 12:
        captains = { 'blue': None, 'red': None }
        rand_num_1 = randint( 0, 11 )
        # Assign blue captain by accessing the player list with random index
        captains['blue'] = players[rand_num_1]
        rand_num_2 = randint( 0, 11 )
        # Keep generating random indicies until we get a different one
        if rand_num_2 is rand_num_1:
            while rand_num_2 is rand_num_1:
                rand_num_2 = randint( 0, 11 )
        captains['red'] = players[rand_num_2]
        return captains
    else:
        return 'Not enough or too many players'


def walk_players(players):
    """
    Adds players to StandardQueue instance.
    If StandardQueue has atleast 2 players in each role, start drafting phase. 
    """
    in_queue = StandardQueue()

    # Iterate over all players in queue..
    for player in players.all():
        if player.role == 'Change me':
            continue
        if in_queue.role_is_filled(player.role):
            print(f'{player.role} has enough players to form a match.')
        in_queue.add_player(player)
    
    # If atleast 2 players are queued for each role in the queue..
    if in_queue.all_roles_filled():
        # Get 12 players from the queue (first two from each role)..
        match_players = in_queue.get_match_players()
        # Choose captains at random..
        captains = choose_captains(match_players)
        # Create Draft Instance
        create_draft(match_players, captains)
        return 'Drafting'
    return None

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

        status = walk_players(queue.players)
        if status == 'Drafting':
            return HttpResponse('Drafting')
        else:
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
        is_in_queue = None

        if pk is not None:
            instance = Token.objects.get(key=request.headers.get(
                'Authorization').split('Token ')[1])
            if Member.objects.get(id=instance.user_id) in Queue.objects.get(id=pk).players.all():
                is_in_queue = True
            else:
                is_in_queue = False

        return Response(data={'is_in_queue': is_in_queue})
