from django.core.validators import RegexValidator
from rest_framework import serializers, status
from members.models import Member

alpha_only = RegexValidator('^[A-Za-z0-9_]+$', message='No unicode')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        exclude = (
            'password', 'email', 'ip_address',
            'groups', 'user_permissions', 'is_staff',
            'first_name', 'last_name', 'is_superuser',
            'last_login', 'date_joined'
        )


class NewMemberSerializer(serializers.Serializer):
    username = serializers.CharField(validators=[alpha_only])
    email = serializers.CharField()
    password = serializers.CharField()
    battle_tag = serializers.CharField()
    role = serializers.CharField()

    # Warcrime function literal kony 2012~
    def create(self, val_data):
        pass_word =val_data.pop('password', None)
        user_name = val_data.pop('username', None)
        battletag = val_data.pop('battle_tag', None)
        player_role = val_data.pop('role', None)
        mail = val_data.pop('email', None)

        does_exist = Member.objects.filter(username__iexact=user_name)
        if len(does_exist) > 0:
            raise serializers.ValidationError('That username already exists.')
            return

        if '@' not in mail or '.' not in mail:
            raise serializers.ValidationError('Please use a proper mailing address.')
            return

        instance = Member(email=mail, username=user_name, battle_tag=battletag, role=player_role)

        if pass_word is not None:
            instance.set_password(pass_word)
        instance.save()

        return instance