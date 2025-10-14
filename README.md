# Bot Discord de Musique pour Pterodactyl

Ce projet contient un bot Discord de musique complet qui peut lire des vidéos YouTube, gérer une file d'attente, et bien plus. Il est conçu pour être déployé facilement sur un panel Pterodactyl à l'aide de l'egg fourni.

## Fonctionnalités

- **Lecture depuis YouTube** : Jouez de la musique via une URL ou une recherche.
- **Système de file d'attente complet** : Ajoutez des musiques, affichez la file d'attente, retirez des éléments, et videz la liste.
- **Commandes de lecture standards** : `play`, `pause`, `resume`, `stop`, `skip`.
- **Contrôle du volume** : Ajustez le volume avec la commande `volume`.
- **Informations en temps réel** : Affichez la musique en cours de lecture avec `nowplaying`.
- **Mode boucle** : Répétez la musique actuelle avec la commande `loop`.
- **Déploiement facile sur Pterodactyl** : Un fichier egg est inclus pour une installation rapide.

## Fichiers Inclus

- `bot.py`: Le code source principal du bot Discord.
- `requirements.txt`: La liste des dépendances Python nécessaires.
- `egg-discord-music-bot.json`: Le fichier de configuration de l'egg pour Pterodactyl.
- `.env.example`: Un exemple de fichier de configuration pour les variables d'environnement.

## Déploiement sur Pterodactyl

1.  **Importer l'egg** : Allez dans la section "Nests" de votre panel Pterodactyl et importez le fichier `egg-discord-music-bot.json`.
2.  **Créer un nouveau serveur** : Créez un nouveau serveur en utilisant l'egg que vous venez d'importer.
3.  **Configurer les variables** : Dans l'onglet "Startup" de votre serveur, remplissez la variable `DISCORD_TOKEN` avec le token de votre bot Discord.
4.  **Démarrer le serveur** : Démarrez le serveur. Pterodactyl installera automatiquement les dépendances et lancera le bot.

## Commandes du Bot

| Commande | Alias | Description |
|---|---|---|
| `play <URL/recherche>` | `p` | Ajoute une musique à la file d'attente. |
| `queue` | `q`, `list` | Affiche la file d'attente actuelle. |
| `skip` | `s` | Passe à la musique suivante. |
| `pause` | | Met en pause la musique. |
| `resume` | | Reprend la musique. |
| `stop` | | Arrête la musique et vide la file d'attente. |
| `clear` | | Vide la file d'attente. |
| `remove <position>` | | Retire une musique de la file d'attente. |
| `nowplaying` | `np`, `now` | Affiche la musique en cours de lecture. |
| `loop` | | Active/désactive la boucle de la musique actuelle. |
| `volume <0-100>` | `vol` | Change le volume de la musique. |
| `leave` | `disconnect`, `dc` | Déconnecte le bot du salon vocal. |
| `ping` | | Affiche la latence du bot. |

