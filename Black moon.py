import discord
from discord.ext import commands, tasks
import requests
import asyncio

# ================= CONFIG =================

TOKEN = "MTQ3MTExMTM3Nzc3ODExNDU2MQ.GwNO90.VTdrljwN2jGdtYB0_CAQxhFePCzYwqWxesNRQk"
OWNER_ID = 909193492536905738

ROBLOX_UNIVERSE_ID = "9707835843"

# ==========================================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =====================================================
# 🔥 FULL SERVER SETUP
# =====================================================

async def full_server_setup(guild):

    # Delete everything
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass

    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
            except:
                pass

    # Roles
    roles_config = {
        "👑 Créateur": (discord.Permissions(administrator=True), discord.Color.gold(), True),
        "🛡️ Gérant Modérateur": (discord.Permissions(manage_guild=True, manage_roles=True, kick_members=True, ban_members=True), discord.Color.red(), True),
        "🛡️ Gérant Support": (discord.Permissions(manage_channels=True, manage_messages=True), discord.Color.dark_red(), True),
        "🎨 Responsable Animation": (discord.Permissions(manage_messages=True), discord.Color.orange(), True),
        "🛡️ Modérateur Senior": (discord.Permissions(manage_messages=True, moderate_members=True), discord.Color.blue(), True),
        "🛡️ Modérateur +": (discord.Permissions(manage_messages=True), discord.Color.blurple(), True),
        "🛡️ Modérateur Confirmé": (discord.Permissions(manage_messages=True), discord.Color.dark_blue(), True),
        "🛡️ Modérateur en Test": (discord.Permissions(manage_messages=True), discord.Color.light_grey(), True),
        "🎧 Support Certifié": (discord.Permissions(manage_messages=True), discord.Color.green(), True),
        "🎧 Support Discord": (discord.Permissions(manage_messages=True), discord.Color.dark_green(), True),
        "🎧 Support Test": (discord.Permissions(manage_messages=True), discord.Color.teal(), True),
        "💎 Donateur (+10000R$)": (discord.Permissions(), discord.Color.purple(), True),
        "💎 Donateur (+3000R$)": (discord.Permissions(), discord.Color.dark_purple(), True),
        "💖 Soutien": (discord.Permissions(), discord.Color.pink(), True),
        "🎓 Étudiant": (discord.Permissions(), discord.Color.light_grey(), True),
        "💎 Premium": (discord.Permissions(priority_speaker=True), discord.Color.magenta(), False),
        "🔴 En Live": (discord.Permissions(priority_speaker=True), discord.Color.red(), False),
    }

    for name, (perms, color, hoist) in roles_config.items():
        await guild.create_role(name=name, permissions=perms, colour=color, hoist=hoist)

    # Categories
    structure = {
        "✨ Accueil": ["👋・bienvenue", "🔗・liens-serveurs", "🔎・preuves"],
        "📚 Informations": ["👮・devenir-modérateur", "👮・devenir-support", "🎥・devenir-vidéaste", "🚀・boosts", "💰・donations"],
        "🎪 Espace Événementielle": ["📢・annonce-event", "📅・planning-event", "💡・boite-à-idées-animations", "📊・sondage-event"],
        "💬 Espace Discussion": ["🌍・discussion", "📷・media", "🎬・content-creator", "⭐・suggestions-bug-question", "⚙️・commande", "📈・trade-exchange"],
        "🔊 Vocal": ["📄・aide-vocal", "🤖・commande-vocal"],
        "❓ Assistance": ["❓・faq", "🎟️・support-ticket"],
        "📢 Live": ["📢・live"],
    }

    for category_name, channels in structure.items():
        category = await guild.create_category(category_name)
        for channel_name in channels:
            await guild.create_text_channel(channel_name, category=category)

    # Vocals
    vocal_cat = discord.utils.get(guild.categories, name="🔊 Vocal")
    await guild.create_voice_channel("🔊 Vocal 1", category=vocal_cat, user_limit=99)
    await guild.create_voice_channel("🔊 Vocal 2", category=vocal_cat, user_limit=99)
    await guild.create_voice_channel("🔊 Vocal 3", category=vocal_cat, user_limit=99)
    await guild.create_voice_channel("➕ Crée ton Vocal", category=vocal_cat)

# =====================================================
# 🎮 ROBLOX STATS AUTO
# =====================================================

@tasks.loop(seconds=60)
async def update_roblox():

    guild = bot.guilds[0]

    url = f"https://games.roblox.com/v1/games?universeIds={ROBLOX_UNIVERSE_ID}"
    response = requests.get(url)

    if response.status_code != 200:
        return

    data = response.json()["data"][0]
    players = data["playing"]
    visits = data["visits"]
    favorites = data["favoritedCount"]

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{players} joueurs en ligne")
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            send_messages=False,
            add_reactions=False
        )
    }

    stats_category = discord.utils.get(guild.categories, name="📊 Statistiques")
    if not stats_category:
        stats_category = await guild.create_category("📊 Statistiques", overwrites=overwrites)

    stats_data = {
        "🎮": f"🎮・Joueurs : {players}",
        "🌍": f"🌍・Visites : {visits}",
        "⭐": f"⭐・Favoris : {favorites}",
    }

    for emoji, new_name in stats_data.items():
        channel = discord.utils.find(lambda c: c.name.startswith(emoji), stats_category.channels)
        if channel:
            await channel.edit(name=new_name)
        else:
            await guild.create_text_channel(new_name, category=stats_category, overwrites=overwrites)

# =====================================================
# 🔊 TEMP VOCAL
# =====================================================

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.name == "➕ Crée ton Vocal":
        category = after.channel.category
        temp = await member.guild.create_voice_channel(f"🔊 Vocal de {member.name}", category=category)
        await member.move_to(temp)

        while True:
            await asyncio.sleep(5)
            if len(temp.members) == 0:
                await temp.delete()
                break

# =====================================================
# 🎓 AUTO ROLE
# =====================================================

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="🎓 Étudiant")
    if role:
        await member.add_roles(role)

# =====================================================
# 🔒 OWNER PANEL
# =====================================================

class OwnerPanel(discord.ui.View):

    @discord.ui.button(label="🔥 Full Setup", style=discord.ButtonStyle.red)
    async def fullsetup_button(self, interaction: discord.Interaction, button):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        await full_server_setup(interaction.guild)
        await interaction.response.send_message("🔥 Structure recréée.", ephemeral=True)

    @discord.ui.button(label="🔄 Force Roblox", style=discord.ButtonStyle.blurple)
    async def force_update(self, interaction: discord.Interaction, button):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        await update_roblox()
        await interaction.response.send_message("✅ Update forcée.", ephemeral=True)

@bot.command()
async def owner(ctx):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Tu n'es pas le propriétaire.")
    await ctx.send("🔒 Panel Owner :", view=OwnerPanel())

# =====================================================
# READY
# =====================================================

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    if not update_roblox.is_running():
        update_roblox.start()

bot.run(TOKEN)
