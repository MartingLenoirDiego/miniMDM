# API miniMDM - Mobile Device Management

## Description

API RESTful pour gérer des appareils mobiles (Devices) organisés en flottes (Fleets). Construite avec Django et Django REST Framework.


## Installation et Démarrage

### Prérequis

- Docker
- Docker Compose

### Lancement

```bash

docker compose up --build

# L'API sera disponible sur http://localhost:8000/api/
```

Le script `entrypoint.sh` crée automatiquement :
- Les migrations de la base de données
- Un superutilisateur de test : `admin` / `admin123`

## Authentification

L'API utilise l'authentification par token JWT. Pour obtenir un token :

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Réponse : {"refresh": "abc123...","access":"def456"}
```

Utilisez ensuite ce token dans toutes vos requêtes :

```bash
curl -H "Authorization: Bearer abc123..." http://localhost:8000/api/users/
```

## Endpoints de l'API

### Users

```
GET /api/users/              # Liste des utilisateurs (soi-même uniquement)
GET /api/users/{id}/         # Détail d'un utilisateur
```

**Exemple de réponse :**

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "date_joined": "2025-01-21T10:00:00Z",
  "fleets": [
    {
      "id": 1,
      "name": "Production Fleet",
      "owner": 1,
      "created_at": "2025-01-21T10:30:00Z"
    }
  ]
}
```

### Fleets

```
GET    /api/fleets/         # Liste des flottes de l'utilisateur
POST   /api/fleets/         # Créer une flotte
GET    /api/fleets/{id}/    # Détail d'une flotte
PUT    /api/fleets/{id}/    # Modifier une flotte
DELETE /api/fleets/{id}/    # Supprimer une flotte
```

**Création d'une Fleet :**

```bash
curl -X POST http://localhost:8000/api/fleets/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{"name": "My Fleet"}'
```

### Devices

```
GET    /api/devices/              # Liste des appareils
GET    /api/devices/?fleet={id}   # Filtrer par flotte
POST   /api/devices/              # Créer un appareil
GET    /api/devices/{id}/         # Détail d'un appareil
PUT    /api/devices/{id}/         # Modifier un appareil
PATCH  /api/devices/{id}/         # Mise à jour partielle
DELETE /api/devices/{id}/         # Supprimer un appareil
```

**Création d'un Device :**

```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "550e8400-e29b-41d4-a716-446655440000",
    "fleet": 1,
    "os_version": 123
  }'
```

**Filtrage par Fleet :**

```bash
curl -H "Authorization: Token abc123..." \
  "http://localhost:8000/api/devices/?fleet=1"
```


## Décisions de Conception

### Pourquoi ces choix ?

1. **JWT Authentication** : Stateless, sécurisé, idéal pour une API REST moderne
   - Tokens avec expiration automatique (access + refresh tokens)

2. **Permissions au niveau ViewSet** : Centralise la logique de sécurité
   - Complété par des validations dans les serializers pour la cohérence

3. **Contrainte unique (name, owner)** : Au niveau DB pour garantir l'intégrité
   - Évite les conditions de course (race conditions)

4. **Filtrage par queryset** : Appliqué automatiquement à tous les endpoints
   - Sécurité par défaut : impossible d'accéder aux données d'un autre user

5. **django-filter** : Pour le filtrage par Fleet sans code custom
   - Extensible facilement pour d'autres filtres

## Logging des Requêtes API

### Vue d'ensemble

L'application inclut un système de logging complet via un middleware personnalisé qui enregistre automatiquement toutes les interactions avec l'API.

**Ce qui est loggé :**
  - **Requêtes entrantes** : Méthode HTTP, URL, utilisateur, IP cliente
  - **Corps des requêtes** : Pour POST/PUT/PATCH (avec masquage des données sensibles)
  - **Réponses** : Status code, temps de traitement
  - **Erreurs détaillées** : Stack traces complètes pour le debugging
  - **Exceptions** : Toutes les erreurs non gérées

**Exemple de sortie :**
```
[INFO] 2025-01-21 14:32:15 | api.requests | [REQUEST] POST /api/auth/token/ | User: Anonymous | IP: 172.18.0.1
[DEBUG] 2025-01-21 14:32:15 | api.requests | [REQUEST BODY] {"username": "admin", "password": "***MASKED***"}
[INFO] 2025-01-21 14:32:15 | api.requests | [RESPONSE] POST /api/auth/token/ | Status: 200 | User: Anonymous | Duration: 0.145s
[INFO] 2025-01-21 14:33:22 | api.requests | [REQUEST] POST /api/fleets/ | User: admin | IP: 172.18.0.1
[INFO] 2025-01-21 14:33:22 | api.requests | [RESPONSE] POST /api/fleets/ | Status: 201 | User: admin | Duration: 0.089s
```

### Fichiers de logs persistants

Les logs sont automatiquement sauvegardés dans le dossier `logs/` de votre projet :

```
~/mini-MDM-API/
├── logs/
│   ├── api_requests.log    # Toutes les requêtes (INFO+)
│   └── errors.log          # Uniquement les erreurs (ERROR uniquement)
```

### Niveaux de log

Les logs sont automatiquement catégorisés par niveau selon le status HTTP :

| Status Code | Niveau | Destination |
|-------------|--------|-------------|
| **200-299** | `INFO` | Console + api_requests.log |
| **400-499** | `WARNING` | Console + api_requests.log |
| **500+** | `ERROR` | Console + api_requests.log + errors.log |


## Améliorations Possibles


- [ ] Pagination optimisée pour de grandes quantités de données
- [ ] Webhooks pour notifier des changements
- [ ] Rate limiting par utilisateur
- [ ] Historique des modifications
- [ ] Soft delete pour les Devices


