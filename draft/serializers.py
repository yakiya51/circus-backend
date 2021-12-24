from rest_framework import serializers
from draft.models import Draft 


class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = '__all__'
