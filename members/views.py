from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from members.models import Member
from members.serializers import MemberSerializer, NewMemberSerializer

from permissions import IsOwnerOrReadOnlyMember


def get_client_ip(request):
    return 'a'
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    # return ip


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = (IsOwnerOrReadOnlyMember,)

    def get_serializer_class(self):
        # if self.request.user.is_authenticated:
            # ip = self.request.META.get('REMOTE_ADDR')
            # _member = Member.objects.get(id=self.request.user.id)
            # _member.ip_address = get_client_ip(self.request)
            # _member.save()

        if self.action == 'create':
            # if 'entrance_key' in self.request.data:
                # ek = EntranceKey.objects.filter(code=self.request.data.get('entrance_key'))
                # if len(ek) > 0:
            return NewMemberSerializer
        else:
            return MemberSerializer

    @action(detail=False, methods=['GET'])
    def sort(self, request):
        if self.request.user.is_authenticated:
            ip = self.request.META.get('REMOTE_ADDR')
            _member = Member.objects.get(id=self.request.user.id)
            _member.ip_address = get_client_ip(self.request)
            _member.save()

        queryset = None

        if 'token' in request.query_params:
            instance = Token.objects.get(key=request.query_params.get('token'))
            queryset = Member.objects.get(id=instance.user_id)
            return Response(MemberSerializer(instance=queryset).data)

        if 'substr' in request.query_params:
            queryset = Member.objects.filter(
                username__contains=request.query_params.get('substr'))

        return Response(MemberSerializer(instance=queryset, many=True).data)


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():

            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})