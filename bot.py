import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os
from collections import deque
from config_manager import ConfigManager

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN', 'MTMyNTU5MjY5MTA1MTg1OTk5OA.GaqqFW.FPfHXifeFThoZukfOZQU_1Pjd9u6LF6uYhcr3c')
DEFAULT_PREFIX = os.getenv('PREFIX', '!')

# Initialiser le gestionnaire de configuration
config_manager = ConfigManager()

# Configuration de youtube_dl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.requester = None

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop_mode = False
        
    def add(self, song):
        self.queue.append(song)
    
    def next(self):
        if self.loop_mode and self.current:
            return self.current
        if len(self.queue) > 0:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None
    
    def clear(self):
        self.queue.clear()
        self.current = None
    
    def remove(self, index):
        if 0 <= index < len(self.queue):
            removed = self.queue[index]
            del self.queue[index]
            return removed
        return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def size(self):
        return len(self.queue)

# Fonction pour obtenir le préfixe dynamique
def get_prefix(bot, message):
    if message.guild:
        return config_manager.get_prefix(message.guild.id)
    return DEFAULT_PREFIX

# Initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Dictionnaire pour stocker les files d'attente par serveur
music_queues = {}

def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()
    return music_queues[guild_id]

async def play_next(ctx):
    """Joue la musique suivante dans la file d'attente"""
    queue = get_queue(ctx.guild.id)
    
    if ctx.voice_client is None:
        return
    
    next_song = queue.next()
    
    if next_song is None:
        await ctx.send("✅ File d'attente terminée !")
        
        # Auto-disconnect si activé
        auto_disconnect = config_manager.get_default_setting(ctx.guild.id, "auto_disconnect")
        if auto_disconnect:
            delay = config_manager.get_default_setting(ctx.guild.id, "auto_disconnect_delay") or 300
            await asyncio.sleep(delay)
            if ctx.voice_client and not ctx.voice_client.is_playing():
                await ctx.voice_client.disconnect()
                await ctx.send("👋 Déconnexion automatique après inactivité")
        return
    
    try:
        player = await YTDLSource.from_url(next_song['url'], loop=bot.loop, stream=True)
        player.requester = next_song['requester']
        
        # Appliquer le volume par défaut
        default_volume = config_manager.get_default_setting(ctx.guild.id, "volume") or 50
        player.volume = default_volume / 100
        
        def after_playing(error):
            if error:
                print(f'Erreur de lecture: {error}')
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        
        ctx.voice_client.play(player, after=after_playing)
        
        duration_str = f"{next_song['duration'] // 60}:{next_song['duration'] % 60:02d}" if next_song['duration'] else "Durée inconnue"
        await ctx.send(f"🎵 Lecture en cours : **{next_song['title']}** [{duration_str}]\nDemandé par : {next_song['requester'].mention}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la lecture : {str(e)}")
        await play_next(ctx)

# Décorateur pour vérifier les permissions personnalisées
def check_custom_permissions():
    async def predicate(ctx):
        # Récupérer le nom original de la commande
        original_name = ctx.command.name
        
        # Vérifier les permissions
        if not config_manager.has_permission(ctx.guild, ctx.author, original_name):
            required_roles = config_manager.get_command_permissions(ctx.guild.id, original_name)
            await ctx.send(f"❌ Vous n'avez pas la permission d'utiliser cette commande. Rôles requis : {', '.join(required_roles)}")
            return False
        return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Game(name=f"{DEFAULT_PREFIX}help | {DEFAULT_PREFIX}music mod"))

@bot.command(name='play', aliases=['p'], help='Ajoute une musique à la file d\'attente')
@check_custom_permissions()
async def play(ctx, *, url):
    """Ajoute une musique à la file d'attente"""
    
    if not ctx.author.voice:
        await ctx.send("❌ Vous devez être dans un salon vocal pour utiliser cette commande.")
        return

    voice_channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    async with ctx.typing():
        try:
            loop = bot.loop
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            song_info = {
                'url': data['webpage_url'],
                'title': data['title'],
                'duration': data.get('duration'),
                'requester': ctx.author
            }
            
            queue = get_queue(ctx.guild.id)
            queue.add(song_info)
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                position = queue.size()
                duration_str = f"{song_info['duration'] // 60}:{song_info['duration'] % 60:02d}" if song_info['duration'] else "Durée inconnue"
                await ctx.send(f"➕ Ajouté à la file d'attente (position {position}) : **{song_info['title']}** [{duration_str}]")
            else:
                await play_next(ctx)
                
        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite : {str(e)}")

@bot.command(name='queue', aliases=['q', 'list'], help='Affiche la file d\'attente')
@check_custom_permissions()
async def queue_command(ctx):
    """Affiche la file d'attente"""
    queue = get_queue(ctx.guild.id)
    
    if queue.current is None and queue.is_empty():
        await ctx.send("📭 La file d'attente est vide.")
        return
    
    embed = discord.Embed(title="🎵 File d'attente", color=discord.Color.blue())
    
    if queue.current:
        duration_str = f"{queue.current['duration'] // 60}:{queue.current['duration'] % 60:02d}" if queue.current['duration'] else "Durée inconnue"
        embed.add_field(
            name="▶️ En cours de lecture",
            value=f"**{queue.current['title']}** [{duration_str}]\nDemandé par : {queue.current['requester'].mention}",
            inline=False
        )
    
    if not queue.is_empty():
        queue_text = ""
        for i, song in enumerate(list(queue.queue)[:10], 1):
            duration_str = f"{song['duration'] // 60}:{song['duration'] % 60:02d}" if song['duration'] else "?"
            queue_text += f"`{i}.` **{song['title']}** [{duration_str}]\n"
        
        embed.add_field(name="📝 À venir", value=queue_text, inline=False)
        
        if queue.size() > 10:
            embed.add_field(name="", value=f"*... et {queue.size() - 10} autre(s) musique(s)*", inline=False)
    
    embed.set_footer(text=f"Total : {queue.size()} musique(s) en attente")
    await ctx.send(embed=embed)

@bot.command(name='skip', aliases=['s'], help='Passe à la musique suivante')
@check_custom_permissions()
async def skip(ctx):
    """Passe à la musique suivante"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Musique passée")
    else:
        await ctx.send("❌ Aucune musique n'est en cours de lecture")

@bot.command(name='pause', help='Met en pause la musique')
@check_custom_permissions()
async def pause(ctx):
    """Met en pause la musique"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Musique mise en pause")
    else:
        await ctx.send("❌ Aucune musique n'est en cours de lecture")

@bot.command(name='resume', help='Reprend la musique')
@check_custom_permissions()
async def resume(ctx):
    """Reprend la musique"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Musique reprise")
    else:
        await ctx.send("❌ Aucune musique n'est en pause")

@bot.command(name='stop', help='Arrête la musique et vide la file d\'attente')
@check_custom_permissions()
async def stop(ctx):
    """Arrête la musique et vide la file d'attente"""
    if ctx.voice_client:
        queue = get_queue(ctx.guild.id)
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⏹️ Musique arrêtée et file d'attente vidée")
    else:
        await ctx.send("❌ Le bot n'est pas connecté à un salon vocal")

@bot.command(name='clear', help='Vide la file d\'attente')
@check_custom_permissions()
async def clear(ctx):
    """Vide la file d'attente"""
    queue = get_queue(ctx.guild.id)
    queue.clear()
    await ctx.send("🗑️ File d'attente vidée")

@bot.command(name='remove', help='Retire une musique de la file d\'attente')
@check_custom_permissions()
async def remove(ctx, position: int):
    """Retire une musique de la file d'attente"""
    queue = get_queue(ctx.guild.id)
    removed = queue.remove(position - 1)
    
    if removed:
        await ctx.send(f"🗑️ Retiré de la file d'attente : **{removed['title']}**")
    else:
        await ctx.send("❌ Position invalide")

@bot.command(name='nowplaying', aliases=['np', 'now'], help='Affiche la musique en cours')
@check_custom_permissions()
async def nowplaying(ctx):
    """Affiche la musique en cours"""
    queue = get_queue(ctx.guild.id)
    
    if queue.current is None:
        await ctx.send("❌ Aucune musique n'est en cours de lecture")
        return
    
    duration_str = f"{queue.current['duration'] // 60}:{queue.current['duration'] % 60:02d}" if queue.current['duration'] else "Durée inconnue"
    
    embed = discord.Embed(title="🎵 Lecture en cours", color=discord.Color.green())
    embed.add_field(name="Titre", value=queue.current['title'], inline=False)
    embed.add_field(name="Durée", value=duration_str, inline=True)
    embed.add_field(name="Demandé par", value=queue.current['requester'].mention, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='loop', help='Active/désactive la boucle de la musique actuelle')
@check_custom_permissions()
async def loop(ctx):
    """Active/désactive la boucle"""
    queue = get_queue(ctx.guild.id)
    queue.loop_mode = not queue.loop_mode
    
    if queue.loop_mode:
        await ctx.send("🔁 Mode boucle activé")
    else:
        await ctx.send("➡️ Mode boucle désactivé")

@bot.command(name='volume', aliases=['vol'], help='Change le volume (0-100)')
@check_custom_permissions()
async def volume(ctx, volume: int):
    """Change le volume de la musique"""
    if ctx.voice_client is None:
        return await ctx.send("❌ Le bot n'est pas connecté à un salon vocal")

    if 0 <= volume <= 100:
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Volume réglé à {volume}%")
    else:
        await ctx.send("❌ Le volume doit être entre 0 et 100")

@bot.command(name='leave', aliases=['disconnect', 'dc'], help='Déconnecte le bot du salon vocal')
@check_custom_permissions()
async def leave(ctx):
    """Déconnecte le bot du salon vocal"""
    if ctx.voice_client:
        queue = get_queue(ctx.guild.id)
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Déconnexion du salon vocal")
    else:
        await ctx.send("❌ Le bot n'est pas connecté à un salon vocal")

@bot.command(name='ping', help='Affiche la latence du bot')
@check_custom_permissions()
async def ping(ctx):
    """Affiche la latence du bot"""
    await ctx.send(f'🏓 Pong! Latence: {round(bot.latency * 1000)}ms')

@bot.command(name='help', help='Affiche la liste des commandes disponibles')
async def help_command(ctx, command_name: str = None):
    """Affiche l'aide des commandes"""
    prefix = config_manager.get_prefix(ctx.guild.id) if ctx.guild else DEFAULT_PREFIX
    
    if command_name:
        # Aide pour une commande spécifique
        cmd = bot.get_command(command_name)
        if cmd:
            embed = discord.Embed(
                title=f"📖 Aide : {prefix}{cmd.name}",
                description=cmd.help or "Aucune description disponible",
                color=discord.Color.blue()
            )
            if cmd.aliases:
                embed.add_field(name="Alias", value=", ".join(f"`{prefix}{a}`" for a in cmd.aliases), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Commande `{command_name}` introuvable")
        return
    
    # Aide générale
    embed = discord.Embed(
        title="🎵 Bot Discord de Musique - Commandes",
        description=f"Préfixe actuel : `{prefix}`\nUtilisez `{prefix}help <commande>` pour plus de détails",
        color=discord.Color.blue()
    )
    
    # Commandes de lecture
    music_commands = [
        ("play <URL/recherche>", "p", "Joue une musique"),
        ("queue", "q, list", "Affiche la file d'attente"),
        ("skip", "s", "Passe à la musique suivante"),
        ("pause", "", "Met en pause"),
        ("resume", "", "Reprend la lecture"),
        ("stop", "", "Arrête et vide la file"),
        ("clear", "", "Vide la file d'attente"),
        ("remove <position>", "", "Retire une musique"),
        ("nowplaying", "np, now", "Musique en cours"),
        ("loop", "", "Active/désactive la boucle"),
        ("volume <0-100>", "vol", "Change le volume"),
        ("leave", "disconnect, dc", "Déconnecte le bot"),
    ]
    
    music_text = "\n".join([f"`{prefix}{cmd}` {f'({aliases})' if aliases else ''} - {desc}" 
                            for cmd, aliases, desc in music_commands])
    embed.add_field(name="🎵 Commandes Musicales", value=music_text, inline=False)
    
    # Commandes utilitaires
    util_commands = [
        ("ping", "Affiche la latence"),
        ("help [commande]", "Affiche cette aide"),
    ]
    
    util_text = "\n".join([f"`{prefix}{cmd}` - {desc}" for cmd, desc in util_commands])
    embed.add_field(name="🔧 Utilitaires", value=util_text, inline=False)
    
    # Commandes de personnalisation
    embed.add_field(
        name="⚙️ Personnalisation (Admins uniquement)",
        value=f"`{prefix}music mod` - Système de personnalisation complet\n"
              f"Changez le préfixe, renommez les commandes, gérez les permissions, etc.",
        inline=False
    )
    
    embed.set_footer(text=f"Pour personnaliser le bot : {prefix}music mod")
    await ctx.send(embed=embed)

# ==================== COMMANDES DE PERSONNALISATION ====================

@bot.group(name='music', help='Commandes de gestion du bot musical')
async def music(ctx):
    """Groupe de commandes pour la gestion du bot"""
    if ctx.invoked_subcommand is None:
        await ctx.send(f"❌ Sous-commande invalide. Utilisez `{config_manager.get_prefix(ctx.guild.id)}music mod` pour la personnalisation.")

@music.command(name='mod', help='Système de personnalisation du bot')
@commands.has_permissions(manage_guild=True)
async def mod(ctx):
    """Affiche l'aide pour la personnalisation"""
    prefix = config_manager.get_prefix(ctx.guild.id)
    
    embed = discord.Embed(
        title="🎛️ Système de Personnalisation du Bot",
        description="Personnalisez le comportement du bot selon vos préférences",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📝 Préfixe",
        value=f"`{prefix}music mod prefix <nouveau_préfixe>`",
        inline=False
    )
    
    embed.add_field(
        name="✏️ Renommer une commande",
        value=f"`{prefix}music mod rename <commande> <nouveau_nom>`",
        inline=False
    )
    
    embed.add_field(
        name="🏷️ Gérer les alias",
        value=f"`{prefix}music mod alias add <commande> <alias>`\n"
              f"`{prefix}music mod alias remove <commande> <alias>`\n"
              f"`{prefix}music mod alias list <commande>`",
        inline=False
    )
    
    embed.add_field(
        name="🔐 Gérer les permissions",
        value=f"`{prefix}music mod perm set <commande> <rôle1> [rôle2...]`\n"
              f"`{prefix}music mod perm clear <commande>`\n"
              f"`{prefix}music mod perm list <commande>`",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Paramètres par défaut",
        value=f"`{prefix}music mod default volume <0-100>`\n"
              f"`{prefix}music mod default loop <on|off>`\n"
              f"`{prefix}music mod default autodisconnect <on|off>`\n"
              f"`{prefix}music mod default autodisconnect_delay <secondes>`",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Utilitaires",
        value=f"`{prefix}music mod show` - Affiche la configuration\n"
              f"`{prefix}music mod reset` - Réinitialise la configuration",
        inline=False
    )
    
    embed.set_footer(text="Seuls les administrateurs peuvent utiliser ces commandes")
    await ctx.send(embed=embed)

@mod.command(name='prefix', help='Change le préfixe du bot')
@commands.has_permissions(manage_guild=True)
async def mod_prefix(ctx, new_prefix: str):
    """Change le préfixe du bot"""
    if len(new_prefix) > 3:
        await ctx.send("❌ Le préfixe ne peut pas dépasser 3 caractères")
        return
    
    if config_manager.set_prefix(ctx.guild.id, new_prefix):
        await ctx.send(f"✅ Préfixe changé en `{new_prefix}`")
    else:
        await ctx.send("❌ Erreur lors du changement de préfixe")

@mod.command(name='rename', help='Renomme une commande')
@commands.has_permissions(manage_guild=True)
async def mod_rename(ctx, command_name: str, new_name: str):
    """Renomme une commande"""
    valid_commands = ['play', 'queue', 'skip', 'pause', 'resume', 'stop', 'clear', 'remove', 'nowplaying', 'loop', 'volume', 'leave', 'ping']
    
    if command_name not in valid_commands:
        await ctx.send(f"❌ Commande invalide. Commandes disponibles : {', '.join(valid_commands)}")
        return
    
    if config_manager.set_command_name(ctx.guild.id, command_name, new_name):
        await ctx.send(f"✅ Commande `{command_name}` renommée en `{new_name}`\n⚠️ Redémarrez le bot pour appliquer les changements")
    else:
        await ctx.send("❌ Erreur lors du renommage (nom invalide)")

@mod.group(name='alias', help='Gère les alias des commandes')
@commands.has_permissions(manage_guild=True)
async def mod_alias(ctx):
    """Groupe de commandes pour gérer les alias"""
    if ctx.invoked_subcommand is None:
        await ctx.send("❌ Sous-commande invalide. Utilisez `add`, `remove` ou `list`")

@mod_alias.command(name='add', help='Ajoute un alias à une commande')
@commands.has_permissions(manage_guild=True)
async def alias_add(ctx, command_name: str, alias: str):
    """Ajoute un alias à une commande"""
    valid_commands = ['play', 'queue', 'skip', 'pause', 'resume', 'stop', 'clear', 'remove', 'nowplaying', 'loop', 'volume', 'leave', 'ping']
    
    if command_name not in valid_commands:
        await ctx.send(f"❌ Commande invalide. Commandes disponibles : {', '.join(valid_commands)}")
        return
    
    if config_manager.add_command_alias(ctx.guild.id, command_name, alias):
        await ctx.send(f"✅ Alias `{alias}` ajouté à la commande `{command_name}`\n⚠️ Redémarrez le bot pour appliquer les changements")
    else:
        await ctx.send("❌ Erreur lors de l'ajout de l'alias (alias invalide ou déjà existant)")

@mod_alias.command(name='remove', help='Retire un alias d\'une commande')
@commands.has_permissions(manage_guild=True)
async def alias_remove(ctx, command_name: str, alias: str):
    """Retire un alias d'une commande"""
    if config_manager.remove_command_alias(ctx.guild.id, command_name, alias):
        await ctx.send(f"✅ Alias `{alias}` retiré de la commande `{command_name}`")
    else:
        await ctx.send("❌ Alias non trouvé")

@mod_alias.command(name='list', help='Liste les alias d\'une commande')
@commands.has_permissions(manage_guild=True)
async def alias_list(ctx, command_name: str):
    """Liste les alias d'une commande"""
    aliases = config_manager.get_command_aliases(ctx.guild.id, command_name)
    
    if aliases:
        await ctx.send(f"📝 Alias de `{command_name}` : {', '.join(f'`{a}`' for a in aliases)}")
    else:
        await ctx.send(f"ℹ️ Aucun alias pour la commande `{command_name}`")

@mod.group(name='perm', help='Gère les permissions des commandes')
@commands.has_permissions(manage_guild=True)
async def mod_perm(ctx):
    """Groupe de commandes pour gérer les permissions"""
    if ctx.invoked_subcommand is None:
        await ctx.send("❌ Sous-commande invalide. Utilisez `set`, `clear` ou `list`")

@mod_perm.command(name='set', help='Définit les rôles autorisés pour une commande')
@commands.has_permissions(manage_guild=True)
async def perm_set(ctx, command_name: str, *roles: str):
    """Définit les rôles autorisés pour une commande"""
    valid_commands = ['play', 'queue', 'skip', 'pause', 'resume', 'stop', 'clear', 'remove', 'nowplaying', 'loop', 'volume', 'leave', 'ping']
    
    if command_name not in valid_commands:
        await ctx.send(f"❌ Commande invalide. Commandes disponibles : {', '.join(valid_commands)}")
        return
    
    if not roles:
        await ctx.send("❌ Vous devez spécifier au moins un rôle")
        return
    
    # Vérifier que les rôles existent
    guild_role_names = [role.name for role in ctx.guild.roles]
    invalid_roles = [r for r in roles if r not in guild_role_names]
    
    if invalid_roles:
        await ctx.send(f"❌ Rôles introuvables : {', '.join(invalid_roles)}")
        return
    
    if config_manager.set_command_permissions(ctx.guild.id, command_name, list(roles)):
        await ctx.send(f"✅ Permissions définies pour `{command_name}` : {', '.join(f'`{r}`' for r in roles)}")
    else:
        await ctx.send("❌ Erreur lors de la définition des permissions")

@mod_perm.command(name='clear', help='Retire toutes les restrictions d\'une commande')
@commands.has_permissions(manage_guild=True)
async def perm_clear(ctx, command_name: str):
    """Retire toutes les restrictions d'une commande"""
    if config_manager.clear_command_permissions(ctx.guild.id, command_name):
        await ctx.send(f"✅ Restrictions retirées pour `{command_name}` (accessible à tous)")
    else:
        await ctx.send("❌ Erreur lors de la suppression des restrictions")

@mod_perm.command(name='list', help='Liste les permissions d\'une commande')
@commands.has_permissions(manage_guild=True)
async def perm_list(ctx, command_name: str):
    """Liste les permissions d'une commande"""
    perms = config_manager.get_command_permissions(ctx.guild.id, command_name)
    
    if perms:
        await ctx.send(f"🔐 Rôles autorisés pour `{command_name}` : {', '.join(f'`{p}`' for p in perms)}")
    else:
        await ctx.send(f"ℹ️ Aucune restriction pour `{command_name}` (accessible à tous)")

@mod.group(name='default', help='Gère les paramètres par défaut')
@commands.has_permissions(manage_guild=True)
async def mod_default(ctx):
    """Groupe de commandes pour gérer les paramètres par défaut"""
    if ctx.invoked_subcommand is None:
        await ctx.send("❌ Sous-commande invalide. Utilisez `volume`, `loop`, `autodisconnect` ou `autodisconnect_delay`")

@mod_default.command(name='volume', help='Définit le volume par défaut')
@commands.has_permissions(manage_guild=True)
async def default_volume(ctx, volume: int):
    """Définit le volume par défaut"""
    if not 0 <= volume <= 100:
        await ctx.send("❌ Le volume doit être entre 0 et 100")
        return
    
    if config_manager.set_default_setting(ctx.guild.id, "volume", volume):
        await ctx.send(f"✅ Volume par défaut défini à {volume}%")
    else:
        await ctx.send("❌ Erreur lors de la définition du volume")

@mod_default.command(name='loop', help='Définit le mode boucle par défaut')
@commands.has_permissions(manage_guild=True)
async def default_loop(ctx, mode: str):
    """Définit le mode boucle par défaut"""
    if mode.lower() not in ['on', 'off']:
        await ctx.send("❌ Mode invalide. Utilisez `on` ou `off`")
        return
    
    enabled = mode.lower() == 'on'
    
    if config_manager.set_default_setting(ctx.guild.id, "loop_mode", enabled):
        await ctx.send(f"✅ Mode boucle par défaut : {'activé' if enabled else 'désactivé'}")
    else:
        await ctx.send("❌ Erreur lors de la définition du mode boucle")

@mod_default.command(name='autodisconnect', help='Active/désactive la déconnexion automatique')
@commands.has_permissions(manage_guild=True)
async def default_autodisconnect(ctx, mode: str):
    """Active/désactive la déconnexion automatique"""
    if mode.lower() not in ['on', 'off']:
        await ctx.send("❌ Mode invalide. Utilisez `on` ou `off`")
        return
    
    enabled = mode.lower() == 'on'
    
    if config_manager.set_default_setting(ctx.guild.id, "auto_disconnect", enabled):
        await ctx.send(f"✅ Déconnexion automatique : {'activée' if enabled else 'désactivée'}")
    else:
        await ctx.send("❌ Erreur lors de la définition de la déconnexion automatique")

@mod_default.command(name='autodisconnect_delay', help='Définit le délai de déconnexion automatique')
@commands.has_permissions(manage_guild=True)
async def default_autodisconnect_delay(ctx, seconds: int):
    """Définit le délai de déconnexion automatique"""
    if seconds < 0:
        await ctx.send("❌ Le délai doit être positif")
        return
    
    if config_manager.set_default_setting(ctx.guild.id, "auto_disconnect_delay", seconds):
        await ctx.send(f"✅ Délai de déconnexion automatique défini à {seconds} secondes")
    else:
        await ctx.send("❌ Erreur lors de la définition du délai")

@mod.command(name='show', help='Affiche la configuration actuelle')
@commands.has_permissions(manage_guild=True)
async def mod_show(ctx):
    """Affiche la configuration actuelle"""
    config = config_manager.get_guild_config(ctx.guild.id)
    
    embed = discord.Embed(
        title="⚙️ Configuration Actuelle",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Préfixe", value=f"`{config['prefix']}`", inline=True)
    
    # Paramètres par défaut
    settings = config.get('default_settings', {})
    embed.add_field(
        name="Paramètres par défaut",
        value=f"Volume: {settings.get('volume', 50)}%\n"
              f"Boucle: {'Activée' if settings.get('loop_mode') else 'Désactivée'}\n"
              f"Auto-déconnexion: {'Activée' if settings.get('auto_disconnect') else 'Désactivée'}\n"
              f"Délai: {settings.get('auto_disconnect_delay', 300)}s",
        inline=True
    )
    
    # Commandes avec permissions
    perms = config.get('permissions', {})
    restricted_commands = {k: v for k, v in perms.items() if v}
    
    if restricted_commands:
        perm_text = "\n".join([f"`{k}`: {', '.join(v)}" for k, v in restricted_commands.items()])
        embed.add_field(name="Commandes restreintes", value=perm_text, inline=False)
    else:
        embed.add_field(name="Commandes restreintes", value="Aucune", inline=False)
    
    await ctx.send(embed=embed)

@mod.command(name='reset', help='Réinitialise la configuration')
@commands.has_permissions(manage_guild=True)
async def mod_reset(ctx):
    """Réinitialise la configuration"""
    if config_manager.reset_guild_config(ctx.guild.id):
        await ctx.send("✅ Configuration réinitialisée aux valeurs par défaut\n⚠️ Redémarrez le bot pour appliquer les changements")
    else:
        await ctx.send("❌ Erreur lors de la réinitialisation")

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        prefix = config_manager.get_prefix(ctx.guild.id) if ctx.guild else DEFAULT_PREFIX
        await ctx.send(f"❌ Commande inconnue. Utilisez `{prefix}help` pour voir les commandes disponibles.")
    elif isinstance(error, commands.MissingRequiredArgument):
        prefix = config_manager.get_prefix(ctx.guild.id) if ctx.guild else DEFAULT_PREFIX
        await ctx.send(f"❌ Argument manquant. Utilisez `{prefix}help {ctx.command}` pour plus d'informations.")
    elif isinstance(error, commands.BadArgument):
        prefix = config_manager.get_prefix(ctx.guild.id) if ctx.guild else DEFAULT_PREFIX
        await ctx.send(f"❌ Argument invalide. Utilisez `{prefix}help {ctx.command}` pour plus d'informations.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande (Gérer le serveur requis)")
    elif isinstance(error, commands.CheckFailure):
        # Erreur déjà gérée par le décorateur check_custom_permissions
        pass
    else:
        await ctx.send(f"❌ Une erreur s'est produite : {str(error)}")
        print(f"Erreur: {error}")

if __name__ == '__main__':
    bot.run(TOKEN)

