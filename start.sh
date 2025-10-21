#!/bin/bash

# Script de démarrage rapide pour le bot Discord de musique

echo "🎵 Bot Discord de Musique - Démarrage"
echo "======================================"
echo ""

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé."
    echo "   Installez Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Vérifier si docker-compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    echo "   Installez Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "   Création à partir de .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Éditez le fichier .env et ajoutez votre DISCORD_TOKEN"
    echo "   Ensuite, relancez ce script."
    exit 1
fi

# Vérifier si le token est configuré
if grep -q "votre_token_discord_ici" .env; then
    echo "⚠️  Le DISCORD_TOKEN n'est pas configuré dans .env"
    echo "   Éditez le fichier .env et remplacez 'votre_token_discord_ici' par votre token Discord"
    exit 1
fi

echo "✅ Configuration vérifiée"
echo ""
echo "🔨 Construction de l'image Docker..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la construction de l'image"
    exit 1
fi

echo ""
echo "🚀 Démarrage du bot..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Bot démarré avec succès!"
    echo ""
    echo "📊 Commandes utiles:"
    echo "   - Voir les logs:        docker-compose logs -f"
    echo "   - Arrêter le bot:       docker-compose down"
    echo "   - Redémarrer le bot:    docker-compose restart"
    echo "   - Voir le statut:       docker-compose ps"
    echo ""
else
    echo "❌ Erreur lors du démarrage du bot"
    exit 1
fi

