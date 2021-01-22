from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from whoYouApi.views import register_user, login_user, ContentViewSet, ContentViewRequestViewSet, WhoYouUserViewSet
from django.conf.urls.static import static
from django.conf import settings

"""Router"""
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'content', ContentViewSet, 'content')
router.register(r'contentViewRequest', ContentViewRequestViewSet, 'contentViewRequest')
router.register(r'users', WhoYouUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    static
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
