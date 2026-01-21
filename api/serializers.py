from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Fleet, Device


class FleetSerializer(serializers.ModelSerializer):
    """Serializer pour les Fleets avec gestion automatique du propriétaire."""
    
    class Meta:
        model = Fleet
        fields = ['id', 'name', 'owner', 'created_at']
        read_only_fields = ['owner', 'created_at']
    
    def create(self, validated_data):
        # Le propriétaire est automatiquement l'utilisateur authentifié
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour les Users incluant leurs Fleets.
    Le mot de passe n'est jamais exposé en lecture.
    """
    fleets = FleetSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'fleets']
        read_only_fields = ['id', 'date_joined']


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les Devices avec validation du propriétaire de la Fleet.
    """
    
    class Meta:
        model = Device
        fields = ['id', 'serial_number', 'fleet', 'os_version', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_fleet(self, fleet):
        """
        Vérifie que la Fleet appartient bien à l'utilisateur authentifié.
        """
        user = self.context['request'].user
        if fleet.owner != user:
            raise serializers.ValidationError(
                "Vous ne pouvez pas assigner un appareil à une flotte qui ne vous appartient pas."
            )
        return fleet
    
    def validate(self, attrs):
        """
        Validation supplémentaire lors de la mise à jour d'un Device.
        Vérifie qu'on ne déplace un Device que vers une Fleet du même propriétaire.
        """
        if self.instance: 
            user = self.context['request'].user
            new_fleet = attrs.get('fleet', self.instance.fleet)
            
            if self.instance.fleet.owner != user or new_fleet.owner != user:
                raise serializers.ValidationError(
                    "Vous ne pouvez déplacer un appareil qu'entre vos propres flottes."
                )
        
        return attrs