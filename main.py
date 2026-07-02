import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import os
import yt_dlp
import asyncio
from discord.ui import View, Select
import time

APPLICATION_CHANNEL_ID = 1474129022731681902

ACCEPT_ROLES = [
    1504770849230557244,
    1482751779107115101
]

PANEL_ENABLED = {"enabled": True}

QUESTIONS = [
    "Why do you want to be a moderator?",
    "How old are you?",
    "Do you have moderation experience?",
    "If yes, which servers have you moderated?",
    "Are you able to host giveaways and boost activity?",
    "Will you reach 800 messages in your first week?",
    "How will you be a better moderator than others?",
    "Anything else you'd like to add?"
]
# ================= MUSIC CONFIGURATION ================= #
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    # ---- BYPASS OPTIONS ----
    'nocheckcertificate': True,
    'geo_bypass': True,
    'cookiefile': 'cookies.txt',  # Keeps your session authenticated
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'],  # Spoofs mobile apps to reduce blocking
            'skip': ['dash', 'hls']
        }
    }
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

warns = {}
sniped_messages = {}


def parse_duration(duration):
    try:
        unit = duration[-1].lower()
        amount = int(duration[:-1])

        if unit == "m":
            return timedelta(minutes=amount)
        elif unit == "h":
            return timedelta(hours=amount)
        elif unit == "d":
            return timedelta(days=amount)
        elif unit == "w":
            return timedelta(weeks=amount)

        return None
    except:
        return None


# ================= HELPER EMBED FUNCTIONS ================= #
def quick_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return

    sniped_messages[message.guild.id] = {
        "author": str(message.author),
        "content": message.content
    }


# ================= WARN ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    warns.setdefault(member.id, []).append(reason)
    embed = quick_embed("⚠️ Member Warned", f"{member.mention} has been warned.\n**Reason:** {reason}", discord.Color.orange())
    await ctx.send(embed=embed)


@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    warns.setdefault(member.id, []).append(reason)
    embed = quick_embed("⚠️ Member Warned", f"{member.mention} has been warned.\n**Reason:** {reason}", discord.Color.orange())
    await interaction.response.send_message(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    user_warns = warns.get(member.id, [])
    if not user_warns:
        return await ctx.send(embed=quick_embed("ℹ️ Warnings", "No warnings found for this member.", discord.Color.light_grey()))
    
    text = "\n".join([f"**{i+1}.** {warn}" for i, warn in enumerate(user_warns)])
    embed = quick_embed(f"📋 Warnings for {member}", text, discord.Color.orange())
    await ctx.send(embed=embed)


@bot.tree.command(name="warnings", description="View warnings")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_warnings(interaction: discord.Interaction, member: discord.Member):
    user_warns = warns.get(member.id, [])
    if not user_warns:
        return await interaction.response.send_message(embed=quick_embed("ℹ️ Warnings", "No warnings found for this member.", discord.Color.light_grey()))
    
    text = "\n".join([f"**{i+1}.** {warn}" for i, warn in enumerate(user_warns)])
    embed = quick_embed(f"📋 Warnings for {member}", text, discord.Color.orange())
    await interaction.response.send_message(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearwarnings(ctx, member: discord.Member):
    warns[member.id] = []
    embed = quick_embed("✅ Warnings Cleared", f"Cleared all warnings for {member.mention}.", discord.Color.green())
    await ctx.send(embed=embed)


@bot.tree.command(name="clearwarnings", description="Clear warnings")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clearwarnings(interaction: discord.Interaction, member: discord.Member):
    warns[member.id] = []
    embed = quick_embed("✅ Warnings Cleared", f"Cleared all warnings for {member.mention}.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


# ================= BAN ================= #

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    embed = quick_embed("🔨 Member Banned", f"Successfully banned **{member}**.\n**Reason:** {reason}", discord.Color.red())
    await ctx.send(embed=embed)


@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.ban(reason=reason)
    embed = quick_embed("🔨 Member Banned", f"Successfully banned **{member}**.\n**Reason:** {reason}", discord.Color.red())
    await interaction.response.send_message(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    embed = quick_embed("✅ User Unbanned", f"Successfully unbanned **{user}**.", discord.Color.green())
    await ctx.send(embed=embed)


@bot.tree.command(name="unban", description="Unban a user")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    embed = quick_embed("✅ User Unbanned", f"Successfully unbanned **{user}**.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


# ================= KICK ================= #

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    embed = quick_embed("👢 Member Kicked", f"Successfully kicked **{member}**.\n**Reason:** {reason}", discord.Color.orange())
    await ctx.send(embed=embed)


@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.kick(reason=reason)
    embed = quick_embed("👢 Member Kicked", f"Successfully kicked **{member}**.\n**Reason:** {reason}", discord.Color.orange())
    await interaction.response.send_message(embed=embed)


# ================= ROLE ================= #

@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
        embed = quick_embed("🛠️ Role Removed", f"Removed {role.mention} from {member.mention}", discord.Color.blue())
    else:
        await member.add_roles(role)
        embed = quick_embed("🛠️ Role Added", f"Added {role.mention} to {member.mention}", discord.Color.blue())
    await ctx.send(embed=embed)


@bot.tree.command(name="role", description="Add or remove a role")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
        embed = quick_embed("🛠️ Role Removed", f"Removed {role.mention} from {member.mention}", discord.Color.blue())
    else:
        await member.add_roles(role)
        embed = quick_embed("🛠️ Role Added", f"Added {role.mention} to {member.mention}", discord.Color.blue())
    await interaction.response.send_message(embed=embed)


# ================= MUTE ================= #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
    td = parse_duration(duration)
    if td is None:
        return await ctx.send(embed=quick_embed("❌ Invalid Duration", "Use durations like: `10m`, `5h`, `2d`, `1w`", discord.Color.red()))
    until = discord.utils.utcnow() + td
    await member.timeout(until, reason=reason)
    embed = quick_embed("🔇 Member Muted", f"Muted {member.mention} for **{duration}**.\n**Reason:** {reason}", discord.Color.dark_grey())
    await ctx.send(embed=embed)


@bot.tree.command(name="mute", description="Mute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):
    td = parse_duration(duration)
    if td is None:
        return await interaction.response.send_message(embed=quick_embed("❌ Invalid Duration", "Use durations like: `10m`, `5h`, `2d`, `1w`", discord.Color.red()), ephemeral=True)
    until = discord.utils.utcnow() + td
    await member.timeout(until, reason=reason)
    embed = quick_embed("🔇 Member Muted", f"Muted {member.mention} for **{duration}**.\n**Reason:** {reason}", discord.Color.dark_grey())
    await interaction.response.send_message(embed=embed)


# ================= UNMUTE ================= #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    embed = quick_embed("🔊 Member Unmuted", f"Successfully unmuted {member.mention}", discord.Color.green())
    await ctx.send(embed=embed)


@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    embed = quick_embed("🔊 Member Unmuted", f"Successfully unmuted {member.mention}", discord.Color.green())
    await interaction.response.send_message(embed=embed)


# ================= PURGE ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    embed = quick_embed("🗑️ Purged Messages", f"Successfully deleted **{amount}** messages.", discord.Color.teal())
    msg = await ctx.send(embed=embed)
    await msg.delete(delay=5)


@bot.tree.command(name="purge", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    embed = quick_embed("🗑️ Purged Messages", f"Successfully deleted **{len(deleted)}** messages.", discord.Color.teal())
    await interaction.followup.send(embed=embed, ephemeral=True)


# ================= LOCK ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = quick_embed("🔒 Channel Locked", "This channel has been locked down.", discord.Color.red())
    await ctx.send(embed=embed)


@bot.tree.command(name="lock", description="Lock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    embed = quick_embed("🔒 Channel Locked", "This channel has been locked down.", discord.Color.red())
    await interaction.response.send_message(embed=embed)


# ================= UNLOCK ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = quick_embed("🔓 Channel Unlocked", "This channel is now unlocked.", discord.Color.green())
    await ctx.send(embed=embed)


@bot.tree.command(name="unlock", description="Unlock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    embed = quick_embed("🔓 Channel Unlocked", "This channel is now unlocked.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


# ================= SLOWMODE ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    embed = quick_embed("🐢 Slowmode Updated", f"Slowmode delay set to **{seconds}** seconds.", discord.Color.gold())
    await ctx.send(embed=embed)


@bot.tree.command(name="slowmode", description="Set channel slowmode")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    embed = quick_embed("🐢 Slowmode Updated", f"Slowmode delay set to **{seconds}** seconds.", discord.Color.gold())
    await interaction.response.send_message(embed=embed)


# ================= SNIPE ================= #

@bot.command()
async def snipe(ctx):
    data = sniped_messages.get(ctx.guild.id)
    if not data:
        return await ctx.send(embed=quick_embed("📭 Snipe", "Nothing to snipe.", discord.Color.light_grey()))
    embed = discord.Embed(title="🎯 Sniped Message", color=discord.Color.blurple())
    embed.add_field(name="Author", value=data["author"], inline=False)
    embed.add_field(name="Message", value=data["content"], inline=False)
    await ctx.send(embed=embed)


@bot.tree.command(name="snipe", description="Show last deleted message")
async def slash_snipe(interaction: discord.Interaction):
    data = sniped_messages.get(interaction.guild.id)
    if not data:
        return await interaction.response.send_message(embed=quick_embed("📭 Snipe", "Nothing to snipe.", discord.Color.light_grey()))
    embed = discord.Embed(title="🎯 Sniped Message", color=discord.Color.blurple())
    embed.add_field(name="Author", value=data["author"], inline=False)
    embed.add_field(name="Message", value=data["content"], inline=False)
    await interaction.response.send_message(embed=embed)


# ================= USERINFO ================= #

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)


@bot.tree.command(name="userinfo", description="View user information")
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 {member}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)


# ================= AVATAR ================= #

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ {member}'s Avatar", color=discord.Color.magenta())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.tree.command(name="avatar", description="View a user's avatar")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"🖼️ {member}'s Avatar", color=discord.Color.magenta())
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ================= SERVERINFO ================= #

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"🏰 {guild.name}", color=discord.Color.green())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.tree.command(name="serverinfo", description="View server information")
async def slash_serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🏰 {guild.name}", color=discord.Color.green())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)


# ================= MEMBERCOUNT ================= #

@bot.command()
async def membercount(ctx):
    embed = quick_embed("👥 Member Count", f"Total members: **{ctx.guild.member_count}**", discord.Color.blurple())
    await ctx.send(embed=embed)


@bot.tree.command(name="membercount", description="View member count")
async def slash_membercount(interaction: discord.Interaction):
    embed = quick_embed("👥 Member Count", f"Total members: **{interaction.guild.member_count}**", discord.Color.blurple())
    await interaction.response.send_message(embed=embed)


# ================= PING ================= #

@bot.command()
async def ping(ctx):
    embed = quick_embed("🏓 Pong!", f"Latency: **{round(bot.latency * 1000)}ms**", discord.Color.dark_green())
    await ctx.send(embed=embed)


@bot.tree.command(name="ping", description="View bot latency")
async def slash_ping(interaction: discord.Interaction):
    embed = quick_embed("🏓 Pong!", f"Latency: **{round(bot.latency * 1000)}ms**", discord.Color.dark_green())
    await interaction.response.send_message(embed=embed)


# ================= SAY ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message):
    await ctx.message.delete()
    embed = quick_embed("", message, discord.Color.blue())
    await ctx.send(embed=embed)


@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_say(interaction: discord.Interaction, message: str):
    embed = quick_embed("", message, discord.Color.blue())
    await interaction.response.send_message(embed=embed)


# ================= POLL ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


@bot.tree.command(name="poll", description="Create a poll")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


# ================= MUSIC COMMANDS ================= #

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send(embed=quick_embed("❌ Error", "You need to be in a voice channel to use this command!", discord.Color.red()))

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    async with ctx.typing():
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        
        if 'entries' in data:
            video = data['entries'][0]
        else:
            video = data

        stream_url = video['url']
        song_title = video['title']

        if voice_client.is_playing():
            voice_client.stop()

        audio_source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(voice_client.disconnect(), bot.loop) if not voice_client.is_playing() else None)

    embed = quick_embed("🎶 Now Playing", f"**{song_title}**", discord.Color.purple())
    await ctx.send(embed=embed)


@bot.tree.command(name="play", description="Joins your voice channel and plays a song!")
@app_commands.describe(query="The name or URL of the song you want to play")
async def slash_play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        return await interaction.response.send_message(embed=quick_embed("❌ Error", "You need to be in a voice channel to use this command!", discord.Color.red()), ephemeral=True)

    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

        if 'entries' in data:
            video = data['entries'][0]
        else:
            video = data

        stream_url = video['url']
        song_title = video['title']

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        if voice_client.is_playing():
            voice_client.stop()

        audio_source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(voice_client.disconnect(), bot.loop) if not voice_client.is_playing() else None)

        embed = quick_embed("🎶 Now Playing", f"**{song_title}**", discord.Color.purple())
        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(e)
        await interaction.followup.send(embed=quick_embed("❌ Error", "An error occurred while trying to play the song.", discord.Color.red()))


@bot.command()
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        embed = quick_embed("👋 Disconnected", "Left the voice channel.", discord.Color.blue())
        await ctx.send(embed=embed)
    else:
        embed = quick_embed("ℹ️ Information", "I am not connected to a voice channel.", discord.Color.light_grey())
        await ctx.send(embed=embed)


@bot.tree.command(name="leave", description="Make the bot leave the voice channel")
async def slash_leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        embed = quick_embed("👋 Disconnected", "Left the voice channel.", discord.Color.blue())
        await interaction.response.send_message(embed=embed)
    else:
        embed = quick_embed("ℹ️ Information", "I am not connected to a voice channel.", discord.Color.light_grey())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ApplicationDecisionView(View):
    def __init__(self, applicant_id):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        member = interaction.guild.get_member(self.applicant_id)

        if member:
            for role_id in ACCEPT_ROLES:
                role = interaction.guild.get_role(role_id)
                if role:
                    await member.add_roles(role)

            try:
                await member.send(
                    embed=quick_embed(
                        "✅ Application Accepted",
                        "Congratulations! Your moderator application has been accepted.",
                        discord.Color.green()
                    )
                )
            except:
                pass

        await interaction.response.send_message(
            embed=quick_embed(
                "✅ Accepted",
                "Application accepted successfully.",
                discord.Color.green()
            ),
            ephemeral=True
        )

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(view=self)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):

        member = interaction.guild.get_member(self.applicant_id)

        if member:
            try:
                await member.send(
                    embed=quick_embed(
                        "❌ Application Denied",
                        "Unfortunately your moderator application was denied.",
                        discord.Color.red()
                    )
                )
            except:
                pass

        await interaction.response.send_message(
            embed=quick_embed(
                "❌ Denied",
                "Application denied.",
                discord.Color.red()
            ),
            ephemeral=True
        )

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(view=self)


class ApplicationDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Moderator Application",
                emoji="🛡️",
                description="Apply for moderator"
            )
        ]

        super().__init__(
            placeholder="Select an application...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if not PANEL_ENABLED["enabled"]:
            return await interaction.response.send_message(
                embed=quick_embed(
                    "❌ Panel Closed",
                    "The panel has been closed by an administrator.",
                    discord.Color.red()
                ),
                ephemeral=True
            )

        await interaction.response.send_message(
            "📩 Check your DMs.",
            ephemeral=True
        )

        user = interaction.user
        answers = []

        try:
            await user.send(
                embed=quick_embed(
                    "Moderator Application",
                    "Please answer all questions."
                )
            )

            def check(m):
                return m.author.id == user.id and isinstance(m.channel, discord.DMChannel)

            start = time.time()

            for i, question in enumerate(QUESTIONS, start=1):
    q_embed = discord.Embed(
        title=f"Question {i}/{len(QUESTIONS)}",
        description=question,
        color=discord.Color.blurple()
    )

    await user.send(embed=q_embed)

    msg = await bot.wait_for(
        "message",
        timeout=600,
        check=check
    )

    answers.append(msg.content) 
    )

    await user.send(embed=q_embed)

                msg = await bot.wait_for(
                    "message",
                    timeout=600,
                    check=check
                )

                answers.append(msg.content)

            end = time.time()

            embed = discord.Embed(
                title="🛡️ Moderator Application",
                color=discord.Color.green()
            )

            for q, a in zip(QUESTIONS, answers):
                embed.add_field(
                    name=q,
                    value=a,
                    inline=False
                )

            embed.add_field(
                name="Applicant",
                value=f"{user.mention}\nID: {user.id}",
                inline=False
            )

            embed.add_field(
                name="Time Taken",
                value=f"{round(end-start)} seconds",
                inline=False
            )

            channel = bot.get_channel(APPLICATION_CHANNEL_ID)

            if channel:
                await channel.send(
                    embed=embed,
                    view=ApplicationDecisionView(user.id)
                )

            await user.send(
                embed=quick_embed(
                    "✅ Submitted",
                    "Your application has been submitted.",
                    discord.Color.green()
                )
            )

        except asyncio.TimeoutError:
            await user.send(
                embed=quick_embed(
                    "❌ Timed Out",
                    "Application timed out.",
                    discord.Color.red()
                )
            )


class ApplicationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ApplicationDropdown())


@bot.tree.command(
    name="modpanel",
    description="Send moderator application panel"
)
@app_commands.checks.has_permissions(administrator=True)
async def modpanel(interaction: discord.Interaction):

    embed = discord.Embed(
    title="🛡️ Moderator Applications",
    description=(
        "**Moderator requirements:**\n"
        "• Must be 13+\n"
        "• Must complete weekly quota for assigned role.\n"
        "• Must be helpful and mature.\n\n"
        "Use the dropdown below to apply."
    ),
    color=discord.Color.blurple()
)
    )

    await interaction.channel.send(
        embed=embed,
        view=ApplicationView()
    )

    await interaction.response.send_message(
        "Panel sent.",
        ephemeral=True
    )


@bot.tree.command(
    name="disablepanel",
    description="Disable application panel"
)
@app_commands.checks.has_permissions(administrator=True)
async def disablepanel(interaction: discord.Interaction):

    PANEL_ENABLED["enabled"] = False

    await interaction.response.send_message(
        embed=quick_embed(
            "❌ Panel Disabled",
            "Applications have been disabled.",
            discord.Color.red()
        ),
        ephemeral=True
    )


@bot.tree.command(
    name="enablepanel",
    description="Enable application panel"
)
@app_commands.checks.has_permissions(administrator=True)
async def enablepanel(interaction: discord.Interaction):

    PANEL_ENABLED["enabled"] = True

    await interaction.response.send_message(
        embed=quick_embed(
            "✅ Panel Enabled",
            "Applications have been enabled.",
            discord.Color.green()
        ),
        ephemeral=True
    )
# ================= ERROR HANDLER ================= #

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = quick_embed("❌ Missing Permissions", "You do not have permission to use this command.", discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = quick_embed("❌ Missing Arguments", "Missing required arguments.", discord.Color.red())
        await ctx.send(embed=embed)


# ================= START BOT ================= #

bot.run(TOKEN)
