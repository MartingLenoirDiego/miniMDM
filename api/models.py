from django.db import models
from django.contrib.auth.models import User


class Fleet(models.Model):
    """
    Représente une flotte d'appareils appartenant à un utilisateur.
    Contrainte : le nom doit être unique par propriétaire.
    """
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='fleets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'owner')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (owned by {self.owner.username})"


class Device(models.Model):
    """
    Représente un appareil mobile.
    Chaque appareil doit obligatoirement appartenir à une Fleet.
    """
    serial_number = models.CharField(max_length=255, unique=True)
    fleet = models.ForeignKey(
        Fleet, 
        on_delete=models.CASCADE, 
        related_name='devices'
    )
    os_version = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['serial_number']
    
    def __str__(self):
        return f"Device {self.serial_number} in {self.fleet.name}"