from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement les propriétaires
    à modifier leurs objets.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user


class IsFleetOwner(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est propriétaire
    de la Fleet associée à un Device.
    """
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'fleet'):
            return obj.fleet.owner == request.user
        return False