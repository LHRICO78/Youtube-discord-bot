import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os
from collections import deque

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN', 'MTMyNTU5MjY5MTA1MTg1OTk5OA.GaqqFW.FPfHXifeFThoZukfOZQU_1Pjd9u6LF6uYhcr3c')
PREFIX = os.getenv('PREFIX', '!')

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
        self.loop_mode = False  # False = pas de boucle, True = boucle la musique actuelle
        
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

# Initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
        return
    
    try:
        player = await YTDLSource.from_url(next_song['url'], loop=bot.loop, stream=True)
        player.requester = next_song['requester']
        
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

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}help"))

@bot.command(name='play', aliases=['p'], help='Ajoute une musique à la file d\'attente')
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
async def skip(ctx):
    """Passe à la musique suivante"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Musique passée")
    else:
        await ctx.send("❌ Aucune musique n'est en cours de lecture")

@bot.command(name='pause', help='Met en pause la musique')
async def pause(ctx):
    """Met en pause la musique"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Musique mise en pause")
    else:
        await ctx.send("❌ Aucune musique n'est en cours de lecture")

@bot.command(name='resume', help='Reprend la musique')
async def resume(ctx):
    """Reprend la musique"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Musique reprise")
    else:
        await ctx.send("❌ Aucune musique n'est en pause")

@bot.command(name='stop', help='Arrête la musique et vide la file d\'attente')
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
async def clear(ctx):
    """Vide la file d'attente"""
    queue = get_queue(ctx.guild.id)
    queue.clear()
    await ctx.send("🗑️ File d'attente vidée")

@bot.command(name='remove', help='Retire une musique de la file d\'attente')
async def remove(ctx, position: int):
    """Retire une musique de la file d'attente"""
    queue = get_queue(ctx.guild.id)
    removed = queue.remove(position - 1)
    
    if removed:
        await ctx.send(f"🗑️ Retiré de la file d'attente : **{removed['title']}**")
    else:
        await ctx.send("❌ Position invalide")

@bot.command(name='nowplaying', aliases=['np', 'now'], help='Affiche la musique en cours')
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
async def loop(ctx):
    """Active/désactive la boucle"""
    queue = get_queue(ctx.guild.id)
    queue.loop_mode = not queue.loop_mode
    
    if queue.loop_mode:
        await ctx.send("🔁 Mode boucle activé")
    else:
        await ctx.send("➡️ Mode boucle désactivé")

@bot.command(name='volume', aliases=['vol'], help='Change le volume (0-100)')
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
async def ping(ctx):
    """Affiche la latence du bot"""
    await ctx.send(f'🏓 Pong! Latence: {round(bot.latency * 1000)}ms')

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Commande inconnue. Utilisez `{PREFIX}help` pour voir les commandes disponibles.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant. Utilisez `{PREFIX}help {ctx.command}` pour plus d'informations.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argument invalide. Utilisez `{PREFIX}help {ctx.command}` pour plus d'informations.")
    else:
        await ctx.send(f"❌ Une erreur s'est produite : {str(error)}")
        print(f"Erreur: {error}")

if __name__ == '__main__':
    bot.run(TOKEN)

