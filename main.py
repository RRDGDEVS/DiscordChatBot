import discord
from discord.ext import commands
from discord import app_commands
from config import TOKEN, GUILD_ID, OWNER_ID
from datetime import datetime, timezone, timedelta

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
MY_GUILD = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="clear", description="Delete your messages in this channel")
async def clear(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=14)
    deleted = 0

    # Collect all messages to delete
    new_msgs = []  # bulk deletable (< 14 days)
    old_msgs = []  # must delete one by one (>= 14 days)

    async for message in interaction.channel.history(limit=None, oldest_first=False):
        if True:
            if message.created_at > cutoff:
                new_msgs.append(message)
            else:
                old_msgs.append(message)

    # Bulk delete new messages in chunks of 100
    for i in range(0, len(new_msgs), 100):
        chunk = new_msgs[i:i+100]
        if len(chunk) == 1:
            await chunk[0].delete()
        else:
            await interaction.channel.delete_messages(chunk)
        deleted += len(chunk)

    # Delete old messages one by one
    for message in old_msgs:
        try:
            await message.delete()
            deleted += 1
        except discord.errors.HTTPException:
            pass

    await interaction.followup.send(f"Done. Deleted {deleted} messages.", ephemeral=True)

bot.run(TOKEN)
