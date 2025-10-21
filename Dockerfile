# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour yt-dlp et FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source du bot
COPY bot.py .
COPY config_manager.py .

# Créer le dossier de configuration
RUN mkdir -p configs

# Définir les variables d'environnement par défaut
ENV DISCORD_TOKEN=""
ENV PREFIX="!"

# Lancer le bot
CMD ["python", "bot.py"]

