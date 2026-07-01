import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import os
import yt_d1p
import asyncio

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

    await ctx.send(
        f"⚠️ {member.mention} has been warned.\nReason: {reason}"
    )


@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_warn(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str
):
    warns.setdefault(member.id, []).append(reason)

    await interaction.response.send_message(
        f"⚠️ {member.mention} has been warned.\nReason: {reason}"
    )


@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    user_warns = warns.get(member.id, [])

    if not user_warns:
        return await ctx.send("No warnings found.")

    text = "\n".join(
        [f"{i+1}. {warn}" for i, warn in enumerate(user_warns)]
    )

    await ctx.send(
        f"Warnings for {member.mention}:\n{text}"
    )


@bot.tree.command(name="warnings", description="View warnings")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_warnings(
    interaction: discord.Interaction,
    member: discord.Member
):
    user_warns = warns.get(member.id, [])

    if not user_warns:
        return await interaction.response.send_message(
            "No warnings found."
        )

    text = "\n".join(
        [f"{i+1}. {warn}" for i, warn in enumerate(user_warns)]
    )

    await interaction.response.send_message(
        f"Warnings for {member.mention}:\n{text}"
    )


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearwarnings(ctx, member: discord.Member):
    warns[member.id] = []
    await ctx.send(f"Cleared warnings for {member.mention}")


@bot.tree.command(
    name="clearwarnings",
    description="Clear warnings"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clearwarnings(
    interaction: discord.Interaction,
    member: discord.Member
):
    warns[member.id] = []
    await interaction.response.send_message(
        f"Cleared warnings for {member.mention}"
    )


# ================= BAN ================= #

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(
    ctx,
    member: discord.Member,
    *,
    reason="No reason provided"
):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member}")


@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str
):
    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 Banned {member}"
    )


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)

    await ctx.guild.unban(user)

    await ctx.send(
        f"✅ Unbanned {user}"
    )


@bot.tree.command(name="unban", description="Unban a user")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(
    interaction: discord.Interaction,
    user_id: str
):
    user = await bot.fetch_user(int(user_id))

    await interaction.guild.unban(user)

    await interaction.response.send_message(
        f"✅ Unbanned {user}"
    )


# ================= KICK ================= #

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(
    ctx,
    member: discord.Member,
    *,
    reason="No reason provided"
):
    await member.kick(reason=reason)

    await ctx.send(
        f"👢 Kicked {member}"
    )


@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str
):
    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 Kicked {member}"
    )
    # ================= ROLE ================= #

@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"Removed {role.name} from {member.mention}")
    else:
        await member.add_roles(role)
        await ctx.send(f"Added {role.name} to {member.mention}")


@bot.tree.command(name="role", description="Add or remove a role")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_role(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):
    if role in member.roles:
        await member.remove_roles(role)
        await interaction.response.send_message(
            f"Removed {role.name} from {member.mention}"
        )
    else:
        await member.add_roles(role)
        await interaction.response.send_message(
            f"Added {role.name} to {member.mention}"
        )


# ================= MUTE ================= #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(
    ctx,
    member: discord.Member,
    duration: str,
    *,
    reason="No reason provided"
):
    td = parse_duration(duration)

    if td is None:
        return await ctx.send(
            "Use durations like: 10m, 5h, 2d, 1w"
        )

    until = discord.utils.utcnow() + td

    await member.timeout(until, reason=reason)

    await ctx.send(
        f"🔇 Muted {member.mention} for {duration}\nReason: {reason}"
    )


@bot.tree.command(name="mute", description="Mute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(
    interaction: discord.Interaction,
    member: discord.Member,
    duration: str,
    reason: str
):
    td = parse_duration(duration)

    if td is None:
        return await interaction.response.send_message(
            "Use durations like: 10m, 5h, 2d, 1w",
            ephemeral=True
        )

    until = discord.utils.utcnow() + td

    await member.timeout(until, reason=reason)

    await interaction.response.send_message(
        f"🔇 Muted {member.mention} for {duration}\nReason: {reason}"
    )


# ================= UNMUTE ================= #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)

    await ctx.send(
        f"🔊 Unmuted {member.mention}"
    )


@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_unmute(
    interaction: discord.Interaction,
    member: discord.Member
):
    await member.timeout(None)

    await interaction.response.send_message(
        f"🔊 Unmuted {member.mention}"
    )


# ================= PURGE ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(
        f"🗑️ Deleted {amount} messages."
    )

    await msg.delete(delay=5)


@bot.tree.command(name="purge", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_purge(
    interaction: discord.Interaction,
    amount: int
):
    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        f"🗑️ Deleted {len(deleted)} messages.",
        ephemeral=True
    )


# ================= LOCK ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)

    overwrite.send_messages = False

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    await ctx.send("🔒 Channel locked.")


@bot.tree.command(name="lock", description="Lock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔒 Channel locked."
    )


# ================= UNLOCK ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)

    overwrite.send_messages = True

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    await ctx.send("🔓 Channel unlocked.")


@bot.tree.command(name="unlock", description="Unlock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = True

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔓 Channel unlocked."
    )


# ================= SLOWMODE ================= #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)

    await ctx.send(
        f"🐢 Slowmode set to {seconds} seconds."
    )


@bot.tree.command(
    name="slowmode",
    description="Set channel slowmode"
)
@app_commands.checks.has_permissions(manage_channels=True)
async def slash_slowmode(
    interaction: discord.Interaction,
    seconds: int
):
    await interaction.channel.edit(
        slowmode_delay=seconds
    )

    await interaction.response.send_message(
        f"🐢 Slowmode set to {seconds} seconds."
    )


# ================= SNIPE ================= #

@bot.command()
async def snipe(ctx):
    data = sniped_messages.get(ctx.guild.id)

    if not data:
        return await ctx.send(
            "Nothing to snipe."
        )

    embed = discord.Embed(
        title="Sniped Message",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Author",
        value=data["author"],
        inline=False
    )

    embed.add_field(
        name="Message",
        value=data["content"],
        inline=False
    )

    await ctx.send(embed=embed)


@bot.tree.command(
    name="snipe",
    description="Show last deleted message"
)
async def slash_snipe(
    interaction: discord.Interaction
):
    data = sniped_messages.get(
        interaction.guild.id
    )

    if not data:
        return await interaction.response.send_message(
            "Nothing to snipe."
        )

    embed = discord.Embed(
        title="Sniped Message",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Author",
        value=data["author"],
        inline=False
    )

    embed.add_field(
        name="Message",
        value=data["content"],
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    ) 
# ================= USERINFO ================= #

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member}",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))

    await ctx.send(embed=embed)


@bot.tree.command(name="userinfo", description="View user information")
async def slash_userinfo(
    interaction: discord.Interaction,
    member: discord.Member = None
):
    member = member or interaction.user

    embed = discord.Embed(
        title=str(member),
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))

    await interaction.response.send_message(embed=embed)


# ================= AVATAR ================= #

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member}'s Avatar"
    )

    embed.set_image(url=member.display_avatar.url)

    await ctx.send(embed=embed)


@bot.tree.command(name="avatar", description="View a user's avatar")
async def slash_avatar(
    interaction: discord.Interaction,
    member: discord.Member = None
):
    member = member or interaction.user

    embed = discord.Embed(
        title=f"{member}'s Avatar"
    )

    embed.set_image(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


# ================= SERVERINFO ================= #

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.green()
    )

    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await ctx.send(embed=embed)


@bot.tree.command(name="serverinfo", description="View server information")
async def slash_serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.green()
    )

    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)


# ================= MEMBERCOUNT ================= #

@bot.command()
async def membercount(ctx):
    await ctx.send(
        f"👥 Members: {ctx.guild.member_count}"
    )


@bot.tree.command(
    name="membercount",
    description="View member count"
)
async def slash_membercount(
    interaction: discord.Interaction
):
    await interaction.response.send_message(
        f"👥 Members: {interaction.guild.member_count}"
    )


# ================= PING ================= #

@bot.command()
async def ping(ctx):
    await ctx.send(
        f"🏓 {round(bot.latency * 1000)}ms"
    )


@bot.tree.command(name="ping", description="View bot latency")
async def slash_ping(
    interaction: discord.Interaction
):
    await interaction.response.send_message(
        f"🏓 {round(bot.latency * 1000)}ms"
    )


# ================= SAY ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)


@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_say(
    interaction: discord.Interaction,
    message: str
):
    await interaction.response.send_message(message)


# ================= POLL ================= #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, question):
    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=discord.Color.gold()
    )

    msg = await ctx.send(embed=embed)

    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


@bot.tree.command(name="poll", description="Create a poll")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_poll(
    interaction: discord.Interaction,
    question: str
):
    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=discord.Color.gold()
    )

    await interaction.response.send_message(
        embed=embed
    )

    msg = await interaction.original_response()

    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


# ================= ERROR HANDLER ================= #

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You do not have permission to use this command."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Missing required arguments."
        )


# ================= START BOT ================= #

bot.run(TOKEN)
