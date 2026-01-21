# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FleetViewSet, DeviceViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'fleets', FleetViewSet, basename='fleet')
router.register(r'devices', DeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
