import os
from typing import Dict, List

import discord
from discord import app_commands
from discord.ext import commands

from generate_image import generate_grid_png

TOKEN = "MTQ3NTQ4MjkzODk1Mzk2MTcwMg.GT2Lba.U-d7WFsPx3UgYaxca-9xwP939iy1wJQdGw_Blo"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store per-server grid
GRIDS: Dict[int, Dict[str, object]] = {}

# Store per-server players (not placed yet)
PLAYERS: Dict[int, List[Dict[str, str]]] = {}

import random

def active_players_with_squares(state, players):
    """
    Returns list of player dicts that are:
      - not eliminated
      - have at least 1 square on the grid
    """
    counts = count_squares_by_label(state["grid"])
    active = []
    for p in players:
        if p.get("eliminated"):
            continue
        label = p.get("label")
        if not label:
            continue
        if counts.get(label, 0) > 0:
            active.append(p)
    return active


def find_adjacent_opponents(state):
    grid = state["grid"]
    height = state["height"]
    width = state["width"]

    random_label = state.get("last_random_label")
    if not random_label:
        return None, []

    opponents = set()

    for y in range(height):
        for x in range(width):
            if grid[y][x] == random_label:
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = grid[ny][nx]
                        if neighbor != "X" and neighbor != random_label:
                            opponents.add(neighbor)

    return random_label, list(opponents)


def count_squares_by_label(grid):
    counts = {}
    for row in grid:
        for cell in row:
            if cell != "X":
                counts[cell] = counts.get(cell, 0) + 1
    return counts


def label_for_user(name: str) -> str:
    # 2-char label for the grid cell
    s = "".join(c for c in name if c.isalnum())
    s = s.upper()
    if len(s) >= 2:
        return s[:2]
    if len(s) == 1:
        return s + "X"
    return "XX"


def build_grid(width: int, height: int) -> List[List[str]]:
    return [["X" for _ in range(width)] for _ in range(height)]


def render_grid(width: int, height: int, grid: List[List[str]]) -> str:
    lines = []
    header = "    " + " ".join(f"{x+1:>2}" for x in range(width))
    lines.append(header)

    for y in range(height):
        row = " ".join(f"{grid[y][x]:>2}" for x in range(width))
        lines.append(f"{y+1:>2}  {row}")

    return "```text\n" + "\n".join(lines) + "\n```"

def make_unique_labels(players: List[Dict[str, str]]) -> List[str]:
    """
    Creates a unique 2-char label per player and stores it in players[i]["label"].
    Strategy:
      base = first 2 alnum chars of name (or pad with X)
      if collision -> DA, D1, D2, ... (still 2 chars)
    """
    used = set()
    labels = []

    for p in players:
        name = p["name"]
        base = "".join(c for c in name if c.isalnum()).upper()
        if len(base) >= 2:
            base2 = base[:2]
        elif len(base) == 1:
            base2 = base + "X"
        else:
            base2 = "XX"

        label = base2
        if label in used:
            first = base2[0] if base2 else "X"
            # try D0..D9 then DA..DZ
            for k in range(10):
                cand = f"{first}{k}"
                if cand not in used:
                    label = cand
                    break
            else:
                for k in range(26):
                    cand = f"{first}{chr(ord('A') + k)}"
                    if cand not in used:
                        label = cand
                        break

        used.add(label)
        p["label"] = label
        labels.append(label)

    return labels


def count_squares_by_label(grid: List[List[str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in grid:
        for cell in row:
            if cell != "X":
                counts[cell] = counts.get(cell, 0) + 1
    return counts


def render_grid_with_legend(state: Dict[str, object], players: List[Dict[str, str]]) -> str:
    width = int(state["width"])
    height = int(state["height"])
    grid: List[List[str]] = state["grid"]  # type: ignore

    # --- grid text ---
    lines = []
    header = "    " + " ".join(f"{x+1:>2}" for x in range(width))
    lines.append(header)

    for y in range(height):
        row = " ".join(f"{grid[y][x]:>2}" for x in range(width))
        lines.append(f"{y+1:>2}  {row}")

    grid_block = "```text\n" + "\n".join(lines) + "\n```"

    # --- legend ---
    counts = count_squares_by_label(grid)

    legend_lines = ["Legend:"]
    # only show players that have a label
    for p in players:
        label = p.get("label")
        if not label:
            continue
        squares = counts.get(label, 0)
        legend_lines.append(f"{label} = {p['name']} — {p['category']} — squares: {squares}")

    # if no labels (game not started yet), show hint
    if len(legend_lines) == 1:
        legend_lines.append("(No labels yet. Run `/floor start` to place users.)")

    return grid_block + "\n" + "\n".join(legend_lines)

def label_to_player(players, label):
    for p in players:
        if p.get("label") == label and not p.get("eliminated"):
            return p
    return None

def adjacent_opponent_labels(state):
    grid = state["grid"]
    width = int(state["width"])
    height = int(state["height"])
    me = state.get("last_random_label")
    if not me:
        return []

    opps = set()
    for y in range(height):
        for x in range(width):
            if grid[y][x] == me:
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        v = grid[ny][nx]
                        if v != "X" and v != me:
                            opps.add(v)
    return sorted(opps)

def transfer_all_squares(state, winner_label, loser_label):
    grid = state["grid"]
    width = int(state["width"])
    height = int(state["height"])
    moved = 0
    for y in range(height):
        for x in range(width):
            if grid[y][x] == loser_label:
                grid[y][x] = winner_label
                moved += 1
    return moved

class OpponentPickView(discord.ui.View):
    def __init__(self, state, players, challenger_label, opponent_labels, host_user_id):
        super().__init__(timeout=60)
        self.state = state
        self.players = players
        self.challenger_label = challenger_label
        self.host_user_id = host_user_id

        for opp_label in opponent_labels[:20]:
            opp = label_to_player(players, opp_label)
            if not opp:
                continue
            self.add_item(OpponentButton(opp_label, f"{opp['name']} ({opp['category']})"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.host_user_id:
            await interaction.response.send_message("Only the host can choose.", ephemeral=True)
            return False
        return True


class OpponentButton(discord.ui.Button):
    def __init__(self, opponent_label: str, label: str):
        super().__init__(label=label[:80], style=discord.ButtonStyle.danger)
        self.opponent_label = opponent_label

    async def callback(self, interaction: discord.Interaction):
        view: OpponentPickView = self.view  # type: ignore
        state = view.state

        state["pending_opponent_label"] = self.opponent_label

        # disable all buttons
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        ch = label_to_player(view.players, view.challenger_label)
        op = label_to_player(view.players, self.opponent_label)

        await interaction.response.edit_message(
            content=(
                f"⚔️ **Duel set!**\n"
                f"Random (challenger): **{ch['name']}** — {ch['category']}\n"
                f"Opponent: **{op['name']}** — {op['category']}\n\n"
                f"Now run `/floor winner` to choose who won."
            ),
            view=view
        )


class WinnerPickView(discord.ui.View):
    def __init__(self, state, players, host_user_id):
        super().__init__(timeout=60)
        self.state = state
        self.players = players
        self.host_user_id = host_user_id

        self.add_item(WinnerButton("random", "Random player won", discord.ButtonStyle.success))
        self.add_item(WinnerButton("opponent", "Opponent won", discord.ButtonStyle.primary))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.host_user_id:
            await interaction.response.send_message("Only the host can choose.", ephemeral=True)
            return False
        return True


class WinnerButton(discord.ui.Button):
    def __init__(self, which: str, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.which = which  # "random" or "opponent"

    async def callback(self, interaction: discord.Interaction):

        if state.get("finished"):
            await interaction.response.send_message("Game is already finished.", ephemeral=True)
            return

        view: WinnerPickView = self.view  # type: ignore
        state = view.state
        players = view.players

        ch_label = state.get("last_random_label")
        op_label = state.get("pending_opponent_label")

        if not ch_label or not op_label:
            await interaction.response.send_message("No duel is set. Run `/floor random` then choose an opponent.", ephemeral=True)
            return

        challenger = label_to_player(players, ch_label)
        opponent = label_to_player(players, op_label)

        if not challenger or not opponent:
            await interaction.response.send_message("One of the duel players is missing/eliminated.", ephemeral=True)
            return

        if self.which == "random":
            winner_label, loser_label = ch_label, op_label
            winner = challenger
            loser = opponent
            # category rule: random won → keep category (no change)
        else:
            winner_label, loser_label = op_label, ch_label
            winner = opponent
            loser = challenger
            # category rule: random lost → opponent inherits random category
            winner["category"] = challenger["category"]

        moved = transfer_all_squares(state, winner_label, loser_label)

        # eliminate loser
        loser["eliminated"] = True

        # clear duel state
        state["pending_opponent_label"] = None

        # --- auto-check end game ---
        active = active_players_with_squares(state, players)
        if len(active) == 1:
            champ = active[0]
            state["finished"] = True

            # Disable buttons
            for child in view.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True

            await interaction.response.edit_message(
                content=(
                    f"🏁 **Winner chosen!**\n"
                    f"Winner: **{winner['name']}** (category: **{winner['category']}**)\n"
                    f"Loser eliminated: **{loser['name']}**\n"
                    f"Squares transferred: **{moved}**\n\n"
                    f"🏆 **GAME OVER!** Champion: **{champ['name']}** (category: **{champ['category']}**)\n"
                    f"Use `/floor show` to see the final grid."
                ),
                view=view
            )
            return
        # disable buttons
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        await interaction.response.edit_message(
            content=(
                f"🏁 **Winner chosen!**\n"
                f"Winner: **{winner['name']}** (category: **{winner['category']}**)\n"
                f"Loser eliminated: **{loser['name']}**\n"
                f"Squares transferred: **{moved}**\n\n"
                f"Use `/floor show` to see the updated grid."
            ),
            view=view
        )

floor = app_commands.Group(name="floor", description="Grid + add user (no placement)")


@floor.command(name="create", description="Create a grid")
@app_commands.describe(width="Grid width (1-30)", height="Grid height (1-30)")
async def floor_create(interaction: discord.Interaction, width: int, height: int):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    if width < 1 or height < 1 or width > 30 or height > 30:
        await interaction.response.send_message("Width/height must be between 1 and 30.", ephemeral=True)
        return

    GRIDS[interaction.guild.id] = {
        "width": width,
        "height": height,
        "grid": build_grid(width, height),
        "finished": False
    }

    # Players list stays as-is (we're not clearing it automatically)
    await interaction.response.send_message(f"✅ Grid created: {width}×{height}")


@floor.command(name="show", description="Show the grid as an image with legend")
async def floor_show(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id
    state = GRIDS.get(gid)
    players = PLAYERS.get(gid, [])

    if not state:
        await interaction.response.send_message("No grid created yet.", ephemeral=True)
        return

    img_buf = generate_grid_png(state)

    await interaction.response.send_message(
        file=discord.File(fp=img_buf, filename="floor_grid.png")
    )


@floor.command(name="add", description="Add a user + category (does not place on grid)")
@app_commands.describe(name="User name (text)", category="Category (text)")
async def floor_add(interaction: discord.Interaction, name: str, category: str):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    # Basic cleaning
    name_clean = " ".join(name.strip().split())
    cat_clean = " ".join(category.strip().split())

    if not name_clean:
        await interaction.response.send_message("Name can't be empty.", ephemeral=True)
        return
    if not cat_clean:
        await interaction.response.send_message("Category can't be empty.", ephemeral=True)
        return

    gid = interaction.guild.id
    players = PLAYERS.setdefault(gid, [])

    # Prevent duplicate names (case-insensitive)
    if any(p["name"].lower() == name_clean.lower() for p in players):
        await interaction.response.send_message(f"User `{name_clean}` already exists.", ephemeral=True)
        return

    players.append({"name": name_clean, "category": cat_clean, "eliminated": False})

    await interaction.response.send_message(
        f"✅ Added user: **{name_clean}** | category: **{cat_clean}**\n"
        f"Total users: **{len(players)}**"
    )

@floor.command(name="start", description="Start game: place users randomly on the grid (fill rest with X)")
async def floor_start(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id

    state = GRIDS.get(gid)
    if not state:
        await interaction.response.send_message("No grid created yet. Use `/floor create`.", ephemeral=True)
        return

    players = PLAYERS.get(gid, [])
    if not players:
        await interaction.response.send_message("No users added yet. Use `/floor add`.", ephemeral=True)
        return

    width = int(state["width"])
    height = int(state["height"])
    total_cells = width * height

    # Create assignments list: user labels + X for empty
    user_labels = make_unique_labels(players)

    msg_lines = []
    if len(user_labels) < total_cells:
        missing = total_cells - len(user_labels)
        msg_lines.append(
            f"⚠️ Not enough users: have **{len(user_labels)}**, need **{total_cells}** → filled **{missing}** with X."
        )
        user_labels.extend(["X"] * missing)
    elif len(user_labels) > total_cells:
        extra = len(user_labels) - total_cells
        msg_lines.append(
            f"⚠️ Too many users: have **{len(user_labels)}**, grid has **{total_cells}** → ignored **{extra}**."
        )
        user_labels = user_labels[:total_cells]

    random.shuffle(user_labels)

    # Build new grid
    grid = []
    idx = 0
    for _y in range(height):
        row = []
        for _x in range(width):
            row.append(user_labels[idx])
            idx += 1
        grid.append(row)

    state["grid"] = grid
    state["finished"] = False

    msg_lines.insert(0, "🎮 **Game started! Users placed randomly.**")
    await interaction.response.send_message("\n".join(msg_lines) + "\n\n" + render_grid_with_legend(state, players))

@floor.command(name="users", description="List users (name + category) with numbering")
async def floor_users(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id
    players = [p for p in PLAYERS.get(gid, []) if not p.get("eliminated")]

    if not players:
        await interaction.response.send_message("No users added yet. Use `/floor add`.", ephemeral=True)
        return

    total = len(players)
    lines = []
    for i, p in enumerate(players, start=1):
        lines.append(f"{i}/{total}. **{p['name']}** — {p['category']}")

    await interaction.response.send_message("\n".join(lines))


@floor.command(name="random", description="Choose a random player (prefer 1-square owner)")
async def floor_random(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id
    state = GRIDS.get(gid)
    players = PLAYERS.get(gid, [])

    if not state:
        await interaction.response.send_message("No grid created yet.", ephemeral=True)
        return

    if not players:
        await interaction.response.send_message("No users added yet.", ephemeral=True)
        return

    grid = state["grid"]

    # Count squares per label
    counts = count_squares_by_label(grid)

    # Only consider players that have a label (game started)
    labeled_players = [p for p in players if "label" in p]

    if not labeled_players:
        await interaction.response.send_message("Game not started yet. Use `/floor start` first.", ephemeral=True)
        return

    # Players with exactly 1 square
    one_square_players = [
        p for p in labeled_players
        if counts.get(p["label"], 0) == 1
    ]

    if one_square_players:
        chosen = random.choice(one_square_players)
        reason = "Player with exactly 1 square selected."
    else:
        chosen = random.choice(labeled_players)
        reason = "No 1-square players. Random player selected."

    state["last_random_label"] = chosen["label"]
    state["host_user_id"] = interaction.user.id
    state["pending_opponent_label"] = None

    squares = counts.get(chosen["label"], 0)

    state["last_random_label"] = chosen["label"] # ???

    await interaction.response.send_message(
        f"🎯 **Random Player Selected**\n"
        f"Name: **{chosen['name']}**\n"
        f"Category: **{chosen['category']}**\n"
        f"Squares: **{squares}**\n\n"
        f"{reason}"
    )

@floor.command(name="fightable", description="Show adjacent opponents for the last random player (with buttons)")
async def floor_fightable(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id
    state = GRIDS.get(gid)
    players = PLAYERS.get(gid, [])

    if not state:
        await interaction.response.send_message("No grid created yet.", ephemeral=True)
        return

    ch_label = state.get("last_random_label")
    host_id = state.get("host_user_id")
    if not ch_label or not host_id:
        await interaction.response.send_message("No random player selected yet. Use `/floor random`.", ephemeral=True)
        return

    challenger = label_to_player(players, ch_label)
    if not challenger:
        await interaction.response.send_message("Random player is missing/eliminated.", ephemeral=True)
        return

    opp_labels = adjacent_opponent_labels(state)
    # remove eliminated/unknown
    opp_labels = [l for l in opp_labels if label_to_player(players, l)]

    if not opp_labels:
        await interaction.response.send_message("🛑 No adjacent opponents available.", ephemeral=False)
        return

    view = OpponentPickView(state, players, ch_label, opp_labels, host_id)
    opp_names = ", ".join(label_to_player(players, l)["name"] for l in opp_labels)

    await interaction.response.send_message(
        f"⚔️ **{challenger['name']}** can duel:\n{opp_names}\n\nChoose opponent:",
        view=view
    )

@floor.command(name="winner", description="Choose the winner of the current duel (buttons)")
async def floor_winner(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Run inside a server.", ephemeral=True)
        return

    gid = interaction.guild.id
    state = GRIDS.get(gid)
    if not state:
        await interaction.response.send_message("No grid created yet.", ephemeral=True)
        return

    if not state.get("last_random_label") or not state.get("pending_opponent_label"):
        await interaction.response.send_message("No duel set. Run `/floor random` then `/floor fightable` and pick an opponent.", ephemeral=True)
        return

    host_id = state.get("host_user_id", interaction.user.id)
    view = WinnerPickView(state, PLAYERS.get(gid, []), host_id)
    await interaction.response.send_message("🏁 Choose the winner:", view=view)


bot.tree.add_command(floor)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_TOKEN environment variable.")
    bot.run(TOKEN)
