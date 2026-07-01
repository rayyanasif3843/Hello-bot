import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

warns = {}
sniped_messages = {}


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
    if not message.author.bot:
        sniped_messages[message.guild.id] = {
            "author": str(message.author),
            "content": message.content
        }


# ---------------- WARN ---------------- #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    warns.setdefault(member.id, []).append(reason)

    embed = discord.Embed(
        title="Member Warned",
        color=discord.Color.orange()
    )
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Reason", value=reason)

    await ctx.send(embed=embed)


@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    warns.setdefault(member.id, []).append(reason)

    embed = discord.Embed(
        title="Member Warned",
        color=discord.Color.orange()
    )
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Reason", value=reason)

    await interaction.response.send_message(embed=embed)


# ---------------- BAN ---------------- #

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member}")


@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member}")


# ---------------- UNBAN ---------------- #

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"Unbanned {user}")


@bot.tree.command(name="unban", description="Unban a user")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"Unbanned {user}")


# ---------------- ROLE ---------------- #

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
async def slash_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
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


# ---------------- MUTE ---------------- #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)
    await ctx.send(f"Muted {member.mention} for {minutes} minute(s)")


@bot.tree.command(name="mute", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(
        f"Muted {member.mention} for {minutes} minute(s)"
    )


# ---------------- UNMUTE ---------------- #

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"Unmuted {member.mention}")


@bot.tree.command(name="unmute", description="Remove timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(
        f"Unmuted {member.mention}"
    )


# ---------------- SNIPE ---------------- #

@bot.command()
async def snipe(ctx):
    data = sniped_messages.get(ctx.guild.id)

    if not data:
        return await ctx.send("Nothing to snipe.")

    embed = discord.Embed(
        title="Sniped Message",
        color=discord.Color.blurple()
    )

    embed.add_field(name="Author", value=data["author"], inline=False)
    embed.add_field(name="Message", value=data["content"], inline=False)

    await ctx.send(embed=embed)


@bot.tree.command(name="snipe", description="Show the last deleted message")
async def slash_snipe(interaction: discord.Interaction):
    data = sniped_messages.get(interaction.guild.id)

    if not data:
        return await interaction.response.send_message("Nothing to snipe.")

    embed = discord.Embed(
        title="Sniped Message",
        color=discord.Color.blurple()
    )

    embed.add_field(name="Author", value=data["author"], inline=False)
    embed.add_field(name="Message", value=data["content"], inline=False)

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)
