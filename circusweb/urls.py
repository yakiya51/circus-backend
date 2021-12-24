from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken import views

from matches.views import MatchViewSet
from matchqueue.views import QueueViewSet
from members.views import MemberViewSet, AuthToken
from matchdraft.views import MatchDraftViewSet

r = routers.DefaultRouter()
r.register(r'members', MemberViewSet)
r.register(r'matches', MatchViewSet)
r.register(r'queue', QueueViewSet)
r.register(r'draft', MatchDraftViewSet)

urlpatterns = [
    path('api/', include(r.urls)),
    path('api/api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('admin/', admin.site.urls),
    path('api-auth/', AuthToken.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)