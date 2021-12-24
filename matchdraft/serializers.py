from rest_framework import serializers
from matchdraft.models import MatchDraft 


class MatchDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchDraft
        fields = '__all__'
