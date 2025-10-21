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
- **🆕 Système de personnalisation complet** : Personnalisez les commandes, permissions et paramètres avec `!music mod`.

## Nouveauté : Système de Personnalisation

Le bot dispose maintenant d'un système de personnalisation avancé permettant aux administrateurs de serveurs de configurer entièrement le comportement du bot.

### Fonctionnalités de Personnalisation

#### 📝 Préfixe Personnalisé
Changez le préfixe du bot pour votre serveur :
```
!music mod prefix ?
```

#### ✏️ Renommer les Commandes
Renommez n'importe quelle commande selon vos préférences :
```
!music mod rename play jouer
!music mod rename queue file
!music mod rename skip passer
```

#### 🏷️ Gestion des Alias
Ajoutez ou retirez des alias pour les commandes :
```
!music mod alias add play j
!music mod alias add queue liste
!music mod alias remove play p
!music mod alias list play
```

#### 🔐 Système de Permissions
Restreignez l'accès aux commandes par rôles Discord :
```
!music mod perm set skip DJ Modérateur
!music mod perm set stop Administrateur
!music mod perm clear play
!music mod perm list skip
```

#### ⚙️ Paramètres par Défaut
Configurez les paramètres par défaut du bot :
```
!music mod default volume 75
!music mod default loop on
!music mod default autodisconnect on
!music mod default autodisconnect_delay 180
```

#### 🔧 Utilitaires
Gérez votre configuration :
```
!music mod show    # Affiche la configuration actuelle
!music mod reset   # Réinitialise aux valeurs par défaut
```

### Permissions Requises

Seuls les utilisateurs avec la permission Discord **"Gérer le serveur"** peuvent utiliser les commandes `!music mod`.

## Fichiers Inclus

- `bot.py`: Le code source principal du bot Discord avec le système de personnalisation.
- `config_manager.py`: Gestionnaire de configuration pour la personnalisation.
- `requirements.txt`: La liste des dépendances Python nécessaires.
- `egg-discord-music-bot.json`: Le fichier de configuration de l'egg pour Pterodactyl.
- `DESIGN.md`: Documentation technique de l'architecture du système de personnalisation.

## Déploiement sur Pterodactyl

1.  **Importer l'egg** : Allez dans la section "Nests" de votre panel Pterodactyl et importez le fichier `egg-discord-music-bot.json`.
2.  **Créer un nouveau serveur** : Créez un nouveau serveur en utilisant l'egg que vous venez d'importer.
3.  **Configurer les variables** : Dans l'onglet "Startup" de votre serveur, remplissez la variable `DISCORD_TOKEN` avec le token de votre bot Discord.
4.  **Démarrer le serveur** : Démarrez le serveur. Pterodactyl installera automatiquement les dépendances et lancera le bot.

## Commandes du Bot

### Commandes Musicales

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
| `help [commande]` | | Affiche la liste des commandes ou l'aide d'une commande spécifique. |

### Commandes de Personnalisation

| Commande | Description |
|---|---|
| `music mod` | Affiche l'aide de personnalisation |
| `music mod prefix <préfixe>` | Change le préfixe du bot |
| `music mod rename <cmd> <nom>` | Renomme une commande |
| `music mod alias add <cmd> <alias>` | Ajoute un alias |
| `music mod alias remove <cmd> <alias>` | Retire un alias |
| `music mod alias list <cmd>` | Liste les alias |
| `music mod perm set <cmd> <rôles...>` | Définit les permissions |
| `music mod perm clear <cmd>` | Retire les restrictions |
| `music mod perm list <cmd>` | Liste les permissions |
| `music mod default volume <0-100>` | Volume par défaut |
| `music mod default loop <on\|off>` | Mode boucle par défaut |
| `music mod default autodisconnect <on\|off>` | Déconnexion auto |
| `music mod default autodisconnect_delay <sec>` | Délai de déconnexion |
| `music mod show` | Affiche la configuration |
| `music mod reset` | Réinitialise la configuration |

## Exemples de Configuration

### Serveur Français
```bash
!music mod prefix ?
?music mod rename play jouer
?music mod alias add jouer j
?music mod rename queue file
?music mod rename skip passer
?music mod default volume 75
```

### Serveur avec Permissions Strictes
```bash
!music mod perm set skip DJ Modérateur
!music mod perm set stop Administrateur
!music mod perm set clear Administrateur
!music mod perm set volume DJ
```

### Serveur Minimaliste
```bash
!music mod prefix .
.music mod alias add play p
.music mod alias add skip s
.music mod alias add queue q
.music mod default autodisconnect on
.music mod default autodisconnect_delay 180
```

## Structure du Projet

```
Youtube-discord-bot/
├── bot.py                  # Fichier principal du bot
├── config_manager.py       # Gestionnaire de configuration
├── configs/                # Dossier des configurations (créé automatiquement)
│   └── guild_configs.json  # Configurations par serveur
├── requirements.txt        # Dépendances Python
├── DESIGN.md              # Documentation technique
├── README.md              # Ce fichier
└── egg-discord-music-bot.json  # Configuration Pterodactyl
```

## Persistance des Configurations

Les configurations sont automatiquement sauvegardées dans le fichier `configs/guild_configs.json` et persistent entre les redémarrages du bot. Chaque serveur Discord a sa propre configuration indépendante.

## Support et Contribution

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur le repository GitHub.

## Licence

Ce projet est open source et disponible sous licence MIT.

