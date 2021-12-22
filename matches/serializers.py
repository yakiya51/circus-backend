from rest_framework import serializers

from matches.models import Match
from members.models import Member
from members.serializers import MemberSerializer


class NestedMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('username',)
        read_only_fields = ('username',)


class MatchSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%A, %D, at %I:%M %p', required=False, read_only=True)
    blue_team = serializers.StringRelatedField(many=True, read_only=True)
    red_team = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Match
        fields = '__all__'
