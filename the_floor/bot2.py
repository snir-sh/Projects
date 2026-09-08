import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import discord
from discord import app_commands
from discord.ext import commands

# Get Discord token from environment variable
# To set it locally: export DISCORD_TOKEN="your-token-here"
# To create a Discord bot token, visit: https://discord.com/developers/applications
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set. Create a bot at https://discord.com/developers/applications")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GRID_W, GRID_H = 4, 4


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class Player:
    user_id: int
    name: str
    category: Optional[str] = None
    alive: bool = True

@dataclass
class FloorGame:
    guild_id: int
    channel_id: int
    status: str = "lobby"  # lobby | running | finished
    players: Dict[int, Player] = field(default_factory=dict)

    # Grid is list of rows, each cell is owner user_id (int)
    grid: List[List[Optional[int]]] = field(default_factory=list)

    # Turn state
    current_challenger_id: Optional[int] = None
    pending_target_id: Optional[int] = None  # chosen opponent for duel
    last_grid_message_id: Optional[int] = None

    def alive_player_ids(self) -> List[int]:
        return [uid for uid, p in self.players.items() if p.alive]

    def owner_cells(self, user_id: int) -> List[Tuple[int, int]]:
        cells = []
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == user_id:
                    cells.append((x, y))
        return cells

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        out = []
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                out.append((nx, ny))
        return out

    def adjacent_enemy_ids(self, user_id: int) -> Set[int]:
        enemies: Set[int] = set()
        for (x, y) in self.owner_cells(user_id):
            for (nx, ny) in self.neighbors(x, y):
                owner = self.grid[ny][nx]
                if owner is not None and owner != user_id and self.players.get(owner) and self.players[owner].alive:
                    enemies.add(owner)
        return enemies

    def capture_all(self, winner_id: int, loser_id: int) -> int:
        """Winner takes all loser cells. Returns number of cells moved."""
        moved = 0
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == loser_id:
                    self.grid[y][x] = winner_id
                    moved += 1
        # eliminate loser if no cells remain
        if len(self.owner_cells(loser_id)) == 0:
            self.players[loser_id].alive = False
        return moved


GAMES: Dict[int, FloorGame] = {}  # guild_id -> game


# -----------------------------
# Helpers
# -----------------------------

def get_game(interaction: discord.Interaction) -> Optional[FloorGame]:
    if not interaction.guild:
        return None
    return GAMES.get(interaction.guild.id)

def render_grid(game: FloorGame) -> str:
    """Render grid as text with short labels."""
    # assign label per user: first 2 chars of name upper, fallback to id suffix
    def label(uid: Optional[int]) -> str:
        if uid is None:
            return "⬜"
        p = game.players.get(uid)
        if not p:
            return "⬜"
        s = "".join([c for c in p.name if c.isalnum()])[:2].upper()
        if len(s) < 2:
            s = (s + "XX")[:2]
        return s

    lines = []
    header = "    " + " ".join([f"{x+1:>2}" for x in range(GRID_W)])
    lines.append(header)
    for y in range(GRID_H):
        row = " ".join([f"{label(game.grid[y][x]):>2}" for x in range(GRID_W)])
        lines.append(f"{y+1:>2}  {row}")
    legend_parts = []
    for uid, p in game.players.items():
        if p.alive:
            tag = "".join([c for c in p.name if c.isalnum()])[:2].upper()
            if len(tag) < 2:
                tag = (tag + "XX")[:2]
            cells = len(game.owner_cells(uid))
            legend_parts.append(f"**{tag}**={p.name} ({cells})")
    legend = " | ".join(legend_parts) if legend_parts else "—"
    return f"```text\n{chr(10).join(lines)}\n```\n{legend}"

async def post_or_edit_grid(channel: discord.abc.Messageable, game: FloorGame) -> None:
    content = "🟦 **THE FLOOR (4×4)**\n" + render_grid(game)

    if game.last_grid_message_id:
        try:
            msg = await channel.fetch_message(game.last_grid_message_id)
            await msg.edit(content=content)
            return
        except Exception:
            game.last_grid_message_id = None

    msg = await channel.send(content)
    game.last_grid_message_id = msg.id

def build_initial_grid(player_ids: List[int]) -> List[List[Optional[int]]]:
    """
    Fill 4x4 = 16 cells.
    If fewer than 16 players, some will get multiple territories.
    """
    cells = []
    # cycle players to fill 16
    for i in range(GRID_W * GRID_H):
        cells.append(player_ids[i % len(player_ids)])
    random.shuffle(cells)
    grid = []
    idx = 0
    for y in range(GRID_H):
        row = []
        for x in range(GRID_W):
            row.append(cells[idx])
            idx += 1
        grid.append(row)
    return grid


# -----------------------------
# UI: Lobby + Category Modal
# -----------------------------

class CategoryModal(discord.ui.Modal, title="Choose your category"):
    category = discord.ui.TextInput(
        label="Your category",
        placeholder="e.g., Marvel, Football, World Capitals...",
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

        uid = interaction.user.id
        if uid not in game.players:
            await interaction.response.send_message("Press **Join** first.", ephemeral=True)
            return

        game.players[uid].category = str(self.category).strip()
        await interaction.response.send_message(
            f"✅ Saved! Your category is: **{game.players[uid].category}**",
            ephemeral=True
        )

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

        uid = interaction.user.id
        if uid in game.players:
            await interaction.response.send_message("You already joined.", ephemeral=True)
            return

        game.players[uid] = Player(user_id=uid, name=interaction.user.display_name)
        await interaction.response.send_message("✅ Joined! Now click **Set Category**.", ephemeral=True)

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
            cat = p.category if p.category else "❓"
            lines.append(f"- **{p.name}** — {cat}")
        msg = "\n".join(lines) if lines else "No one joined yet."
        await interaction.response.send_message(f"**Lobby ({len(players)}):**\n{msg}", ephemeral=True)


# -----------------------------
# UI: Challenger chooses adjacent opponent
# -----------------------------

class ChallengeView(discord.ui.View):
    def __init__(self, game: FloorGame, challenger_id: int, enemy_ids: List[int]):
        super().__init__(timeout=60)
        self.game = game
        self.challenger_id = challenger_id

        # create one button per enemy
        for eid in enemy_ids[:5]:  # keep it small; for 4x4 it's fine
            name = self.game.players[eid].name
            self.add_item(ChallengeButton(eid, label=f"Challenge {name}"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.challenger_id:
            await interaction.response.send_message("Only the current challenger can choose.", ephemeral=True)
            return False
        return True

class ChallengeButton(discord.ui.Button):
    def __init__(self, enemy_id: int, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.danger)
        self.enemy_id = enemy_id

    async def callback(self, interaction: discord.Interaction):
        view: ChallengeView = self.view  # type: ignore
        game = view.game

        if game.status != "running" or game.current_challenger_id != view.challenger_id:
            await interaction.response.send_message("This challenge is no longer valid.", ephemeral=True)
            return

        game.pending_target_id = self.enemy_id
        challenger = game.players[view.challenger_id]
        target = game.players[self.enemy_id]

        await interaction.response.send_message(
            f"⚔️ **Duel set!**\n"
            f"Challenger: **{challenger.name}**\n"
            f"Target: **{target.name}** (category: **{target.category}**)\n\n"
            f"Referee: resolve with `/floor win @winner`",
            ephemeral=False
        )
        # disable buttons after selection
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.message.edit(view=view)  # type: ignore


# -----------------------------
# Slash Commands
# -----------------------------

floor = app_commands.Group(name="floor", description="The Floor game commands")


@floor.command(name="create", description="Create a new Floor lobby in this channel")
async def floor_create(interaction: discord.Interaction):
    if not interaction.guild or not interaction.channel:
        await interaction.response.send_message("Run this in a server channel.", ephemeral=True)
        return

    gid = interaction.guild.id
    GAMES[gid] = FloorGame(guild_id=gid, channel_id=interaction.channel.id, status="lobby")

    await interaction.response.send_message(
        "🟦 **The Floor (4×4) Lobby created!**\nClick **Join** then **Set Category**.\nWhen ready: `/floor start`",
        view=LobbyView(guild_id=gid)
    )


@floor.command(name="start", description="Start the game and build the 4x4 grid")
async def floor_start(interaction: discord.Interaction):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game:
        await interaction.response.send_message("No lobby found. Use `/floor create`.", ephemeral=True)
        return
    if game.status != "lobby":
        await interaction.response.send_message("Game already started.", ephemeral=True)
        return

    players = list(game.players.values())
    if len(players) < 2:
        await interaction.response.send_message("Need at least 2 players.", ephemeral=True)
        return

    missing = [p.name for p in players if not p.category]
    if missing:
        await interaction.response.send_message(
            "These players must set a category first:\n" + "\n".join(f"- {m}" for m in missing),
            ephemeral=True
        )
        return

    game.status = "running"
    alive_ids = game.alive_player_ids()
    game.grid = build_initial_grid(alive_ids)

    await interaction.response.send_message("✅ **Game started!** Use `/floor turn` to pick a challenger.")
    await post_or_edit_grid(interaction.channel, game)


@floor.command(name="turn", description="Pick a random challenger and let them choose an adjacent opponent")
async def floor_turn(interaction: discord.Interaction):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game or game.status != "running":
        await interaction.response.send_message("No running game.", ephemeral=True)
        return

    # reset pending duel
    game.pending_target_id = None

    # pick challengers who have at least one adjacent enemy
    candidates = []
    for uid in game.alive_player_ids():
        if len(game.owner_cells(uid)) > 0 and len(game.adjacent_enemy_ids(uid)) > 0:
            candidates.append(uid)

    if not candidates:
        await interaction.response.send_message("No valid challenger found (game may be finished).", ephemeral=True)
        return

    challenger_id = random.choice(candidates)
    game.current_challenger_id = challenger_id
    enemies = sorted(list(game.adjacent_enemy_ids(challenger_id)))

    challenger = game.players[challenger_id]
    enemy_names = ", ".join(game.players[e].name for e in enemies)

    await interaction.response.send_message(
        f"🎯 **Challenger:** {challenger.name}\nAdjacent opponents: {enemy_names}\nChoose one:",
        view=ChallengeView(game=game, challenger_id=challenger_id, enemy_ids=enemies)
    )


@floor.command(name="win", description="Resolve the duel: winner captures all territories of the loser (referee/admin)")
@app_commands.describe(winner="The winner of the duel (must be challenger or target)")
async def floor_win(interaction: discord.Interaction, winner: discord.Member):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game or game.status != "running":
        await interaction.response.send_message("No running game.", ephemeral=True)
        return

    if not game.current_challenger_id or not game.pending_target_id:
        await interaction.response.send_message("No duel to resolve. Use `/floor turn` first.", ephemeral=True)
        return

    ch = game.current_challenger_id
    tg = game.pending_target_id

    if winner.id not in {ch, tg}:
        await interaction.response.send_message("Winner must be the challenger or the chosen target.", ephemeral=True)
        return

    loser_id = tg if winner.id == ch else ch

    moved = game.capture_all(winner.id, loser_id)

    # finish check
    alive_with_cells = [uid for uid in game.alive_player_ids() if len(game.owner_cells(uid)) > 0]
    if len(alive_with_cells) <= 1:
        game.status = "finished"
        champ = game.players[alive_with_cells[0]].name if alive_with_cells else "Unknown"
        await interaction.response.send_message(f"🏆 **Game finished!** Winner: **{champ}**")
        await post_or_edit_grid(interaction.channel, game)
        return

    # clear turn state
    game.current_challenger_id = None
    game.pending_target_id = None

    await interaction.response.send_message(
        f"✅ **{game.players[winner.id].name} wins!** Captured {moved} cell(s) from {game.players[loser_id].name}.\n"
        f"Next: `/floor turn`"
    )
    await post_or_edit_grid(interaction.channel, game)


@floor.command(name="grid", description="Repost/refresh the grid message")
async def floor_grid(interaction: discord.Interaction):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game or not game.grid:
        await interaction.response.send_message("No grid yet.", ephemeral=True)
        return
    await interaction.response.send_message("Refreshing grid…", ephemeral=True)
    await post_or_edit_grid(interaction.channel, game)


bot.tree.add_command(floor)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (id={bot.user.id})")




# -------
BOT_CATEGORIES = [
    "Movies", "TV", "Geography", "Sports", "Music", "History",
    "Marvel", "Gaming", "Food", "Science"
]

def next_bot_id(game: FloorGame) -> int:
    """Return a unique negative id for a new bot player."""
    used = set(game.players.keys())
    bot_id = -1
    while bot_id in used:
        bot_id -= 1
    return bot_id

def add_bot_players(game: FloorGame, count: int) -> List[int]:
    """Add count bot players into lobby. Returns their ids."""
    new_ids = []
    for i in range(count):
        uid = next_bot_id(game)
        bot_num = abs(uid)  # 1,2,3...
        name = f"BOT {bot_num}"
        cat = random.choice(BOT_CATEGORIES)

        game.players[uid] = Player(user_id=uid, name=name, category=cat, alive=True)
        new_ids.append(uid)
    return new_ids

# --
@floor.command(name="addbot", description="Add bot players to the lobby for testing")
@app_commands.describe(count="How many bot players to add")
async def floor_addbot(interaction: discord.Interaction, count: int):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game:
        await interaction.response.send_message("No lobby found. Use `/floor create` first.", ephemeral=True)
        return

    if game.status != "lobby":
        await interaction.response.send_message("You can only add bots before the game starts (during lobby).", ephemeral=True)
        return

    if count < 1 or count > 20:
        await interaction.response.send_message("Choose a count between 1 and 20.", ephemeral=True)
        return

    ids = add_bot_players(game, count)
    names = ", ".join(game.players[i].name for i in ids)

    await interaction.response.send_message(
        f"🤖 Added {count} bot(s): {names}\nThey already have categories. Now run `/floor start`.",
        ephemeral=False
    )
#--
class WinnerChoice(app_commands.Choice[str]):
    pass

@floor.command(name="resolve", description="Resolve the current duel by choosing who won (challenger/target)")
@app_commands.choices(winner=[
    app_commands.Choice(name="challenger", value="challenger"),
    app_commands.Choice(name="target", value="target"),
])
async def floor_resolve(interaction: discord.Interaction, winner: app_commands.Choice[str]):
    game = get_game(interaction)
    if not interaction.guild or not interaction.channel or not game or game.status != "running":
        await interaction.response.send_message("No running game.", ephemeral=True)
        return

    if not game.current_challenger_id or not game.pending_target_id:
        await interaction.response.send_message("No duel to resolve. Use `/floor turn` first.", ephemeral=True)
        return

    ch = game.current_challenger_id
    tg = game.pending_target_id

    winner_id = ch if winner.value == "challenger" else tg
    loser_id = tg if winner_id == ch else ch

    moved = game.capture_all(winner_id, loser_id)

    # finish check
    alive_with_cells = [uid for uid in game.alive_player_ids() if len(game.owner_cells(uid)) > 0]
    if len(alive_with_cells) <= 1:
        game.status = "finished"
        champ = game.players[alive_with_cells[0]].name if alive_with_cells else "Unknown"
        await interaction.response.send_message(f"🏆 **Game finished!** Winner: **{champ}**")
        await post_or_edit_grid(interaction.channel, game)
        return

    # clear turn state
    game.current_challenger_id = None
    game.pending_target_id = None

    await interaction.response.send_message(
        f"✅ **{game.players[winner_id].name} wins!** Captured {moved} cell(s) from {game.players[loser_id].name}.\n"
        f"Next: `/floor turn`"
    )
    await post_or_edit_grid(interaction.channel, game)
#------



if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_TOKEN env var.")
    bot.run(TOKEN)