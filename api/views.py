from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from .models import Fleet, Device
from .serializers import UserSerializer, FleetSerializer, DeviceSerializer
from .permissions import IsOwnerOrReadOnly, IsFleetOwner


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la lecture des Users.
    Les utilisateurs authentifiés ne peuvent voir que leur propre profil.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class FleetViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des Fleets.
    Les utilisateurs ne peuvent voir et gérer que leurs propres Fleets.
    """
    serializer_class = FleetSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Fleet.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion complète des Devices (CRUD).
    Les utilisateurs ne peuvent gérer que les Devices dans leurs Fleets.
    Filtrage par Fleet disponible via le paramètre ?fleet=<fleet_id>
    """
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, IsFleetOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fleet']
    
    def get_queryset(self):
        return Device.objects.filter(fleet__owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Surcharge pour vérifier que l'utilisateur possède au moins une Fleet
        avant de créer un Device.
        """
        user_fleets = Fleet.objects.filter(owner=request.user).exists()
        if not user_fleets:
            return Response(
                {"detail": "Vous devez posséder au moins une flotte pour créer un appareil."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)