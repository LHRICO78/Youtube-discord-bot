# Guide d'Utilisation du Système de Personnalisation

## Introduction

Ce guide vous explique comment utiliser le système de personnalisation du bot Discord de musique. Vous pourrez personnaliser entièrement le comportement du bot pour l'adapter à votre serveur.

## Prérequis

- Avoir la permission Discord **"Gérer le serveur"** pour utiliser les commandes de personnalisation
- Le bot doit être invité sur votre serveur avec les permissions appropriées

## Commande Principale

Toutes les commandes de personnalisation commencent par :
```
!music mod
```

Pour voir l'aide complète :
```
!music mod
```

## 1. Changer le Préfixe

### Syntaxe
```
!music mod prefix <nouveau_préfixe>
```

### Exemples
```bash
# Changer le préfixe en ?
!music mod prefix ?

# Changer le préfixe en .
!music mod prefix .

# Changer le préfixe en !!
!music mod prefix !!
```

### Limitations
- Le préfixe ne peut pas dépasser 3 caractères
- Le préfixe ne peut pas être vide

### Après le changement
Une fois le préfixe changé, toutes les commandes utiliseront le nouveau préfixe :
```
?play https://youtube.com/...
?queue
?skip
```

## 2. Renommer les Commandes

### Syntaxe
```
!music mod rename <commande> <nouveau_nom>
```

### Commandes disponibles
- `play` - Jouer une musique
- `queue` - Afficher la file d'attente
- `skip` - Passer à la musique suivante
- `pause` - Mettre en pause
- `resume` - Reprendre la lecture
- `stop` - Arrêter la musique
- `clear` - Vider la file d'attente
- `remove` - Retirer une musique
- `nowplaying` - Musique en cours
- `loop` - Mode boucle
- `volume` - Régler le volume
- `leave` - Déconnecter le bot
- `ping` - Tester la latence

### Exemples
```bash
# Renommer play en jouer
!music mod rename play jouer

# Renommer queue en file
!music mod rename queue file

# Renommer skip en passer
!music mod rename skip passer

# Renommer nowplaying en encours
!music mod rename nowplaying encours
```

### Important
⚠️ **Après avoir renommé des commandes, vous devez redémarrer le bot pour que les changements prennent effet.**

### Utilisation après renommage
```
!jouer https://youtube.com/...
!file
!passer
```

## 3. Gérer les Alias

Les alias sont des raccourcis alternatifs pour les commandes.

### Ajouter un alias
```
!music mod alias add <commande> <alias>
```

### Exemples
```bash
# Ajouter l'alias "j" pour play
!music mod alias add play j

# Ajouter l'alias "liste" pour queue
!music mod alias add queue liste

# Ajouter l'alias "p" pour pause
!music mod alias add pause p
```

### Retirer un alias
```
!music mod alias remove <commande> <alias>
```

### Exemples
```bash
# Retirer l'alias "p" de play
!music mod alias remove play p

# Retirer l'alias "s" de skip
!music mod alias remove skip s
```

### Lister les alias
```
!music mod alias list <commande>
```

### Exemples
```bash
# Voir tous les alias de play
!music mod alias list play

# Voir tous les alias de queue
!music mod alias list queue
```

### Important
⚠️ **Après avoir ajouté/retiré des alias, vous devez redémarrer le bot pour que les changements prennent effet.**

## 4. Gérer les Permissions

Vous pouvez restreindre l'accès à certaines commandes par rôles Discord.

### Définir les permissions
```
!music mod perm set <commande> <rôle1> [rôle2] [rôle3]...
```

### Exemples
```bash
# Seuls les DJ peuvent skip
!music mod perm set skip DJ

# Seuls les DJ et Modérateurs peuvent skip
!music mod perm set skip DJ Modérateur

# Seuls les Administrateurs peuvent stop
!music mod perm set stop Administrateur

# Seuls les DJ peuvent changer le volume
!music mod perm set volume DJ

# Seuls les Administrateurs peuvent clear la queue
!music mod perm set clear Administrateur
```

### Retirer les restrictions
```
!music mod perm clear <commande>
```

### Exemples
```bash
# Tout le monde peut utiliser skip
!music mod perm clear skip

# Tout le monde peut utiliser play
!music mod perm clear play
```

### Lister les permissions
```
!music mod perm list <commande>
```

### Exemples
```bash
# Voir qui peut utiliser skip
!music mod perm list skip

# Voir qui peut utiliser stop
!music mod perm list stop
```

### Important
- Les noms de rôles sont sensibles à la casse
- Les rôles doivent exister sur votre serveur
- Si aucune restriction n'est définie, tout le monde peut utiliser la commande

## 5. Paramètres par Défaut

### Volume par défaut
Définit le volume initial lors de la lecture d'une musique.

```
!music mod default volume <0-100>
```

### Exemples
```bash
# Volume par défaut à 50%
!music mod default volume 50

# Volume par défaut à 75%
!music mod default volume 75

# Volume par défaut à 100%
!music mod default volume 100
```

### Mode boucle par défaut
Active ou désactive le mode boucle par défaut.

```
!music mod default loop <on|off>
```

### Exemples
```bash
# Activer le mode boucle par défaut
!music mod default loop on

# Désactiver le mode boucle par défaut
!music mod default loop off
```

### Déconnexion automatique
Le bot se déconnecte automatiquement après un certain temps d'inactivité.

```
!music mod default autodisconnect <on|off>
```

### Exemples
```bash
# Activer la déconnexion automatique
!music mod default autodisconnect on

# Désactiver la déconnexion automatique
!music mod default autodisconnect off
```

### Délai de déconnexion automatique
Définit le délai en secondes avant la déconnexion automatique.

```
!music mod default autodisconnect_delay <secondes>
```

### Exemples
```bash
# Déconnexion après 5 minutes (300 secondes)
!music mod default autodisconnect_delay 300

# Déconnexion après 3 minutes (180 secondes)
!music mod default autodisconnect_delay 180

# Déconnexion après 10 minutes (600 secondes)
!music mod default autodisconnect_delay 600
```

## 6. Utilitaires

### Afficher la configuration actuelle
```
!music mod show
```

Affiche un résumé de toute la configuration de votre serveur :
- Préfixe actuel
- Paramètres par défaut (volume, boucle, auto-déconnexion)
- Commandes avec restrictions de permissions

### Réinitialiser la configuration
```
!music mod reset
```

Réinitialise toute la configuration aux valeurs par défaut.

⚠️ **Cette action est irréversible !**

## Scénarios d'Utilisation

### Scénario 1 : Serveur Français

Vous voulez adapter le bot pour un serveur francophone :

```bash
# Changer le préfixe
!music mod prefix ?

# Renommer les commandes en français
?music mod rename play jouer
?music mod rename queue file
?music mod rename skip passer
?music mod rename pause pause
?music mod rename resume reprendre
?music mod rename stop arreter
?music mod rename clear vider
?music mod rename nowplaying encours
?music mod rename leave partir

# Ajouter des alias courts
?music mod alias add jouer j
?music mod alias add file f
?music mod alias add passer p

# Paramètres
?music mod default volume 75
```

### Scénario 2 : Serveur avec Rôle DJ

Vous voulez que seuls les DJ puissent contrôler la musique :

```bash
# Créer des restrictions
!music mod perm set skip DJ
!music mod perm set pause DJ
!music mod perm set resume DJ
!music mod perm set stop DJ
!music mod perm set clear DJ
!music mod perm set volume DJ

# Les commandes suivantes restent accessibles à tous
# - play (tout le monde peut ajouter des musiques)
# - queue (tout le monde peut voir la file)
# - nowplaying (tout le monde peut voir ce qui joue)
```

### Scénario 3 : Serveur Strict

Vous voulez un contrôle total par les administrateurs :

```bash
# Tout restreindre aux Administrateurs
!music mod perm set play Administrateur
!music mod perm set skip Administrateur
!music mod perm set pause Administrateur
!music mod perm set resume Administrateur
!music mod perm set stop Administrateur
!music mod perm set clear Administrateur
!music mod perm set volume Administrateur
!music mod perm set leave Administrateur

# Seules les commandes d'information restent publiques
# - queue
# - nowplaying
# - ping
```

### Scénario 4 : Serveur Minimaliste

Vous voulez un bot simple avec des commandes courtes :

```bash
# Préfixe court
!music mod prefix .

# Alias ultra-courts
.music mod alias add play p
.music mod alias add queue q
.music mod alias add skip s
.music mod alias add pause pa
.music mod alias add resume r
.music mod alias add nowplaying np
.music mod alias add leave l

# Auto-déconnexion pour économiser les ressources
.music mod default autodisconnect on
.music mod default autodisconnect_delay 180
```

## FAQ

### Q : Puis-je avoir des préfixes différents sur différents serveurs ?
**R :** Oui ! Chaque serveur a sa propre configuration indépendante.

### Q : Que se passe-t-il si je renomme une commande avec un nom déjà utilisé ?
**R :** Le nouveau nom écrasera l'ancien. Faites attention aux conflits de noms.

### Q : Les alias peuvent-ils entrer en conflit avec d'autres commandes ?
**R :** Oui, évitez d'utiliser des alias qui sont déjà des noms de commandes.

### Q : Puis-je exporter ma configuration pour l'utiliser sur un autre serveur ?
**R :** Actuellement, chaque serveur doit être configuré individuellement. Une fonction d'export/import sera ajoutée dans une future version.

### Q : Que se passe-t-il si je supprime un rôle utilisé dans les permissions ?
**R :** Le bot continuera de chercher ce rôle. Vous devrez mettre à jour les permissions manuellement.

### Q : Comment revenir à la configuration par défaut ?
**R :** Utilisez la commande `!music mod reset`.

### Q : Les modifications sont-elles sauvegardées après un redémarrage du bot ?
**R :** Oui, toutes les configurations sont sauvegardées dans un fichier JSON et persistent entre les redémarrages.

## Support

Pour toute question ou problème, consultez le README.md ou ouvrez une issue sur le repository GitHub.

## Résumé des Commandes

| Catégorie | Commande | Description |
|-----------|----------|-------------|
| **Préfixe** | `!music mod prefix <préfixe>` | Change le préfixe |
| **Renommer** | `!music mod rename <cmd> <nom>` | Renomme une commande |
| **Alias** | `!music mod alias add <cmd> <alias>` | Ajoute un alias |
| | `!music mod alias remove <cmd> <alias>` | Retire un alias |
| | `!music mod alias list <cmd>` | Liste les alias |
| **Permissions** | `!music mod perm set <cmd> <rôles...>` | Définit les permissions |
| | `!music mod perm clear <cmd>` | Retire les restrictions |
| | `!music mod perm list <cmd>` | Liste les permissions |
| **Défauts** | `!music mod default volume <0-100>` | Volume par défaut |
| | `!music mod default loop <on\|off>` | Mode boucle par défaut |
| | `!music mod default autodisconnect <on\|off>` | Déconnexion auto |
| | `!music mod default autodisconnect_delay <sec>` | Délai de déconnexion |
| **Utilitaires** | `!music mod show` | Affiche la configuration |
| | `!music mod reset` | Réinitialise la configuration |

