# bot.py
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

app_id = "1475482938953961702"
public_key = "06368237dbc5c0c08c3e2e996d69ed90d3f384c8918a951735bae1c79015ce42"
token = "MTQ3NTQ4MjkzODk1Mzk2MTcwMg.GT2Lba.U-d7WFsPx3UgYaxca-9xwP939iy1wJQdGw_Blo"

# TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
# If you later need full member lists, enable members intent in dev portal + here:
# intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# In-memory state (replace with SQLite later)
# -----------------------------

@dataclass
class LobbyPlayer:
    user_id: int
    display_name: str
    category: Optional[str] = None

@dataclass
class FloorGame:
    guild_id: int
    channel_id: int
    status: str = "lobby"  # lobby | running | finished
    players: Dict[int, LobbyPlayer] = field(default_factory=dict)

GAMES: Dict[int, FloorGame] = {}  # guild_id -> game


# -----------------------------
# UI: Category modal
# -----------------------------

class CategoryModal(discord.ui.Modal, title="Choose your category"):
    category = discord.ui.TextInput(
        label="Your category",
        placeholder="e.g., Marvel, Football, 90s Music, World Capitals...",
        max_length=40
    )

    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        game = GAMES.get(self.guild_id)
        if not game or game.status != "lobby":
            await interaction.response.send_message("No active lobby to join.", ephemeral=True)
            return

        user = interaction.user
        lp = game.players.get(user.id)
        if not lp:
            await interaction.response.send_message("Press **Join** first.", ephemeral=True)
            return

        lp.category = str(self.category).strip()
        await interaction.response.send_message(
            f"✅ Saved! Your category is: **{lp.category}**",
            ephemeral=True
        )


# -----------------------------
# UI: Lobby view with buttons
# -----------------------------

class LobbyView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, custom_id="floor_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = GAMES.get(self.guild_id)
        if not game or game.status != "lobby":
            await interaction.response.send_message("No active lobby.", ephemeral=True)
            return

        user = interaction.user
        if user.id in game.players:
            await interaction.response.send_message("You already joined. Use **Set Category**.", ephemeral=True)
            return

        game.players[user.id] = LobbyPlayer(user_id=user.id, display_name=user.display_name)
        await interaction.response.send_message(
            "✅ Joined the lobby! Now click **Set Category**.",
            ephemeral=True
        )

    @discord.ui.button(label="Set Category", style=discord.ButtonStyle.primary, custom_id="floor_category")
    async def set_category(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = GAMES.get(self.guild_id)
        if not game or game.status != "lobby":
            await interaction.response.send_message("No active lobby.", ephemeral=True)
            return

        if interaction.user.id not in game.players:
            await interaction.response.send_message("Press **Join** first.", ephemeral=True)
            return

        await interaction.response.send_modal(CategoryModal(guild_id=self.guild_id))

    @discord.ui.button(label="Lobby Status", style=discord.ButtonStyle.secondary, custom_id="floor_status")
    async def status(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = GAMES.get(self.guild_id)
        if not game:
            await interaction.response.send_message("No game created.", ephemeral=True)
            return

        players = list(game.players.values())
        lines = []
        for p in players:
            cat = p.category if p.category else "❓ (no category yet)"
            lines.append(f"- **{p.display_name}** — {cat}")

        msg = "\n".join(lines) if lines else "No one joined yet."
        await interaction.response.send_message(
            f"**Lobby players ({len(players)}):**\n{msg}",
            ephemeral=True
        )


# -----------------------------
# Slash commands
# -----------------------------

floor = app_commands.Group(name="floor", description="The Floor game commands")

@floor.command(name="create", description="Create a new Floor lobby in this channel")
async def floor_create(interaction: discord.Interaction):
    if not interaction.guild or not interaction.channel:
        await interaction.response.send_message("Run this in a server channel.", ephemeral=True)
        return

    gid = interaction.guild.id
    GAMES[gid] = FloorGame(guild_id=gid, channel_id=interaction.channel.id, status="lobby")

    view = LobbyView(guild_id=gid)
    await interaction.response.send_message(
        "🟦 **The Floor Lobby created!**\nClick **Join** then **Set Category**.\n(When ready, use `/floor start`.)",
        view=view
    )

@floor.command(name="start", description="Start the game (basic validation only for now)")
async def floor_start(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run this in a server.", ephemeral=True)
        return

    game = GAMES.get(interaction.guild.id)
    if not game or game.status != "lobby":
        await interaction.response.send_message("No active lobby. Use `/floor create`.", ephemeral=True)
        return

    players = list(game.players.values())
    if len(players) < 4:
        await interaction.response.send_message("Need at least 4 players to start (for now).", ephemeral=True)
        return

    missing = [p.display_name for p in players if not p.category]
    if missing:
        await interaction.response.send_message(
            "These players must set a category first:\n" + "\n".join(f"- {m}" for m in missing),
            ephemeral=True
        )
        return

    game.status = "running"
    await interaction.response.send_message(
        "✅ Game started! Next step: build grid + random challenger + adjacency duel UI."
    )

bot.tree.add_command(floor)

@bot.event
async def on_ready():
    # Sync commands to guilds faster during development:
    # await bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (id={bot.user.id})")

if __name__ == "__main__":
    # if not TOKEN:
        # raise RuntimeError("Set DISCORD_TOKEN env var.")
    bot.run(token)