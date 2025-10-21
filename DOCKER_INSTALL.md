# Installation avec Docker

Ce guide vous explique comment installer et exécuter le bot Discord de musique avec Docker.

## Prérequis

- **Docker** installé sur votre système ([Guide d'installation](https://docs.docker.com/get-docker/))
- **Docker Compose** installé ([Guide d'installation](https://docs.docker.com/compose/install/))
- Un **token Discord** pour votre bot ([Comment obtenir un token](https://discord.com/developers/applications))

## Installation Rapide

### 1. Cloner le Repository

```bash
git clone https://github.com/LHRICO78/Youtube-discord-bot.git
cd Youtube-discord-bot
```

### 2. Configurer le Token Discord

Copiez le fichier d'exemple et éditez-le :

```bash
cp .env.example .env
nano .env  # ou utilisez votre éditeur préféré
```

Remplacez `votre_token_discord_ici` par votre véritable token Discord :

```env
DISCORD_TOKEN=MTMyNTU5MjY5MTA1MTg1OTk5OA.GaqqFW.FPfHXifeFThoZukfOZQU_1Pjd9u6LF6uYhcr3c
PREFIX=!
```

### 3. Démarrer le Bot

#### Option A : Script de démarrage automatique (Recommandé)

```bash
./start.sh
```

Ce script va :
- Vérifier que Docker et Docker Compose sont installés
- Vérifier que le fichier `.env` est configuré
- Construire l'image Docker
- Démarrer le bot en arrière-plan

#### Option B : Commandes manuelles

```bash
# Construire l'image Docker
docker-compose build

# Démarrer le bot en arrière-plan
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f
```

## Gestion du Bot

### Voir les Logs

```bash
# Logs en temps réel
docker-compose logs -f

# Dernières 100 lignes
docker-compose logs --tail=100

# Logs depuis les 5 dernières minutes
docker-compose logs --since 5m
```

### Arrêter le Bot

```bash
docker-compose down
```

### Redémarrer le Bot

```bash
docker-compose restart
```

### Mettre à Jour le Bot

```bash
# Récupérer les dernières modifications
git pull

# Reconstruire l'image
docker-compose build

# Redémarrer avec la nouvelle version
docker-compose down
docker-compose up -d
```

### Voir le Statut

```bash
docker-compose ps
```

## Structure des Fichiers

```
Youtube-discord-bot/
├── Dockerfile              # Configuration de l'image Docker
├── docker-compose.yml      # Configuration Docker Compose
├── .env                    # Configuration (TOKEN, PREFIX)
├── .env.example           # Exemple de configuration
├── start.sh               # Script de démarrage rapide
├── bot.py                 # Code principal du bot
├── config_manager.py      # Gestionnaire de configuration
├── requirements.txt       # Dépendances Python
└── configs/               # Configurations des serveurs (persisté)
    └── guild_configs.json
```

## Persistance des Données

Les configurations des serveurs Discord sont automatiquement sauvegardées dans le dossier `configs/` qui est monté comme volume Docker. Cela signifie que vos personnalisations (préfixes, commandes renommées, permissions, etc.) sont conservées même après un redémarrage du conteneur.

## Configuration Avancée

### Limites de Ressources

Par défaut, le bot est limité à :
- **CPU** : 1 cœur maximum, 0.5 cœur réservé
- **RAM** : 512 MB maximum, 256 MB réservé

Pour modifier ces limites, éditez le fichier `docker-compose.yml` :

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'        # Augmenter à 2 cœurs
      memory: 1G         # Augmenter à 1 GB
    reservations:
      cpus: '1.0'
      memory: 512M
```

### Variables d'Environnement

Vous pouvez ajouter d'autres variables dans le fichier `.env` :

```env
DISCORD_TOKEN=votre_token
PREFIX=!
# Ajoutez vos propres variables ici
```

### Réseau Docker

Par défaut, le bot utilise le réseau Docker par défaut. Pour utiliser un réseau personnalisé :

```yaml
services:
  discord-music-bot:
    # ... configuration existante ...
    networks:
      - mon_reseau

networks:
  mon_reseau:
    driver: bridge
```

## Dépannage

### Le bot ne démarre pas

1. **Vérifier les logs** :
   ```bash
   docker-compose logs
   ```

2. **Vérifier que le token est correct** :
   ```bash
   cat .env
   ```

3. **Vérifier que le conteneur est en cours d'exécution** :
   ```bash
   docker-compose ps
   ```

### Le bot se déconnecte constamment

Cela peut être dû à un token invalide ou expiré. Vérifiez votre token sur le [portail développeur Discord](https://discord.com/developers/applications).

### Erreur "ffmpeg not found"

L'image Docker inclut déjà FFmpeg. Si vous rencontrez cette erreur, reconstruisez l'image :

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Problème de permissions sur le dossier configs/

```bash
# Donner les permissions au dossier
chmod -R 755 configs/

# Redémarrer le bot
docker-compose restart
```

### Le bot ne répond pas aux commandes

1. Vérifiez que le bot a les bonnes permissions sur Discord
2. Vérifiez que les intents sont activés dans le portail Discord :
   - Message Content Intent
   - Server Members Intent (optionnel)

### Nettoyer les conteneurs et images

```bash
# Arrêter et supprimer le conteneur
docker-compose down

# Supprimer l'image
docker rmi youtube-discord-bot_discord-music-bot

# Nettoyer tous les conteneurs arrêtés
docker container prune

# Nettoyer toutes les images non utilisées
docker image prune -a
```

## Déploiement en Production

### Utiliser Docker Swarm

```bash
# Initialiser Swarm
docker swarm init

# Déployer le stack
docker stack deploy -c docker-compose.yml music-bot

# Voir les services
docker stack services music-bot

# Voir les logs
docker service logs music-bot_discord-music-bot
```

### Utiliser Kubernetes

Un fichier de déploiement Kubernetes peut être créé :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: discord-music-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: discord-music-bot
  template:
    metadata:
      labels:
        app: discord-music-bot
    spec:
      containers:
      - name: bot
        image: votre-registry/discord-music-bot:latest
        env:
        - name: DISCORD_TOKEN
          valueFrom:
            secretKeyRef:
              name: discord-bot-secret
              key: token
        volumeMounts:
        - name: configs
          mountPath: /app/configs
      volumes:
      - name: configs
        persistentVolumeClaim:
          claimName: bot-configs-pvc
```

## Sécurité

### Bonnes Pratiques

1. **Ne commitez jamais le fichier .env** - Il contient votre token Discord
2. **Utilisez des secrets Docker** pour le token en production :
   ```bash
   echo "votre_token" | docker secret create discord_token -
   ```
3. **Limitez les ressources** pour éviter les abus
4. **Mettez à jour régulièrement** l'image Docker
5. **Surveillez les logs** pour détecter les comportements anormaux

### Utiliser Docker Secrets (Production)

```yaml
version: '3.8'

services:
  discord-music-bot:
    image: discord-music-bot:latest
    secrets:
      - discord_token
    environment:
      - DISCORD_TOKEN_FILE=/run/secrets/discord_token

secrets:
  discord_token:
    external: true
```

## Support

Pour toute question ou problème :
- Consultez les [Issues GitHub](https://github.com/LHRICO78/Youtube-discord-bot/issues)
- Consultez le [README.md](README.md)
- Consultez le [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)

## Licence

Ce projet est open source et disponible sous licence MIT.

