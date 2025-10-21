# Architecture du Système de Personnalisation

## Vue d'ensemble

Ce document décrit l'architecture du système de personnalisation pour le bot Discord de musique. Le système permettra aux administrateurs de serveurs de personnaliser complètement le comportement du bot via la commande `!music mod`.

## Composants Principaux

### 1. Système de Configuration (config.json)

Un fichier JSON par serveur stockera toutes les personnalisations :

```json
{
  "guild_id": {
    "prefix": "!",
    "command_names": {
      "play": "play",
      "queue": "queue",
      "skip": "skip",
      ...
    },
    "command_aliases": {
      "play": ["p", "jouer"],
      "queue": ["q", "list", "liste"],
      ...
    },
    "permissions": {
      "play": [],
      "skip": ["DJ", "Modérateur"],
      "stop": ["Administrateur"],
      ...
    },
    "default_settings": {
      "volume": 50,
      "loop_mode": false,
      "auto_disconnect": true,
      "auto_disconnect_delay": 300
    }
  }
}
```

### 2. Gestionnaire de Configuration (ConfigManager)

Une classe Python qui gère :
- Chargement/sauvegarde de la configuration
- Validation des modifications
- Accès thread-safe aux paramètres
- Valeurs par défaut pour les nouveaux serveurs

### 3. Système de Commandes Dynamiques

Le bot utilisera un système de commandes dynamiques qui :
- Charge les noms de commandes depuis la configuration
- Applique les alias personnalisés
- Vérifie les permissions avant l'exécution
- Applique les paramètres par défaut

### 4. Commande !music mod

Interface principale de personnalisation avec sous-commandes :

#### Sous-commandes disponibles :

**Gestion du préfixe :**
- `!music mod prefix <nouveau_préfixe>` - Modifie le préfixe du bot

**Gestion des noms de commandes :**
- `!music mod rename <commande> <nouveau_nom>` - Renomme une commande
- `!music mod alias add <commande> <alias>` - Ajoute un alias
- `!music mod alias remove <commande> <alias>` - Retire un alias
- `!music mod alias list <commande>` - Liste les alias d'une commande

**Gestion des permissions :**
- `!music mod perm set <commande> <rôle1> [rôle2...]` - Définit les rôles autorisés
- `!music mod perm clear <commande>` - Retire toutes les restrictions
- `!music mod perm list <commande>` - Affiche les permissions d'une commande

**Paramètres par défaut :**
- `!music mod default volume <0-100>` - Volume par défaut
- `!music mod default loop <on|off>` - Mode boucle par défaut
- `!music mod default autodisconnect <on|off>` - Déconnexion automatique
- `!music mod default autodisconnect_delay <secondes>` - Délai de déconnexion

**Utilitaires :**
- `!music mod show` - Affiche toute la configuration actuelle
- `!music mod reset` - Réinitialise la configuration par défaut
- `!music mod export` - Exporte la configuration en JSON
- `!music mod import <json>` - Importe une configuration

## Structure des Fichiers

```
Youtube-discord-bot/
├── bot.py                  # Fichier principal (modifié)
├── config_manager.py       # Nouveau : Gestionnaire de configuration
├── command_handler.py      # Nouveau : Système de commandes dynamiques
├── configs/                # Nouveau : Dossier des configurations
│   └── guild_configs.json  # Configurations par serveur
├── requirements.txt        # Dépendances (mise à jour)
└── README.md              # Documentation (mise à jour)
```

## Flux de Fonctionnement

### Démarrage du Bot

1. Le bot charge le `ConfigManager`
2. Le `ConfigManager` charge toutes les configurations de serveurs
3. Pour chaque serveur, les commandes sont enregistrées avec leurs noms/alias personnalisés
4. Le bot démarre avec les configurations chargées

### Exécution d'une Commande

1. Un utilisateur envoie un message avec une commande
2. Le système vérifie le préfixe personnalisé du serveur
3. Le système identifie la commande via son nom ou alias personnalisé
4. Le système vérifie les permissions de l'utilisateur
5. Si autorisé, la commande s'exécute avec les paramètres par défaut du serveur
6. Sinon, un message d'erreur est envoyé

### Modification de Configuration

1. Un administrateur utilise `!music mod`
2. Le système vérifie que l'utilisateur a la permission "Gérer le serveur"
3. La modification est validée (format, valeurs acceptables)
4. La configuration est mise à jour en mémoire
5. La configuration est sauvegardée dans le fichier JSON
6. Les commandes sont rechargées dynamiquement si nécessaire
7. Un message de confirmation est envoyé

## Sécurité et Permissions

### Permissions Requises pour !music mod

Seuls les utilisateurs avec la permission Discord "Gérer le serveur" peuvent utiliser `!music mod`.

### Validation des Entrées

- Les préfixes sont limités à 1-3 caractères
- Les noms de commandes doivent être alphanumériques (snake_case accepté)
- Les alias ne peuvent pas entrer en conflit avec d'autres commandes
- Les rôles doivent exister sur le serveur
- Les valeurs numériques sont validées (volume 0-100, délai > 0)

### Persistance des Données

- Sauvegarde automatique après chaque modification
- Backup automatique avant import de configuration
- Gestion des erreurs de lecture/écriture avec fallback sur valeurs par défaut

## Compatibilité et Migration

### Rétrocompatibilité

- Les serveurs sans configuration utilisent les valeurs par défaut
- L'ancien système de préfixe via variable d'environnement est conservé comme fallback
- Les commandes existantes fonctionnent sans modification

### Migration

Lors de la première utilisation de `!music mod`, une configuration par défaut est créée automatiquement pour le serveur.

## Exemples d'Utilisation

### Exemple 1 : Serveur Français

```
!music mod prefix ?
!music mod rename play jouer
!music mod alias add jouer j
!music mod rename queue file
!music mod rename skip passer
!music mod default volume 75
```

### Exemple 2 : Serveur avec Permissions Strictes

```
!music mod perm set skip DJ Modérateur
!music mod perm set stop Administrateur
!music mod perm set clear Administrateur
!music mod perm set volume DJ
```

### Exemple 3 : Serveur Minimaliste

```
!music mod prefix .
!music mod alias add play p
!music mod alias add skip s
!music mod alias add queue q
!music mod default autodisconnect on
!music mod default autodisconnect_delay 180
```

## Améliorations Futures Possibles

- Interface web pour la configuration
- Templates de configuration prédéfinis
- Statistiques d'utilisation des commandes
- Logs des modifications de configuration
- Système de rôles DJ automatique
- Limites de file d'attente par utilisateur
- Blacklist/whitelist de sources audio

