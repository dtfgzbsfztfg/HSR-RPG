"""
스토리 진행을 담당하는 Cog.
- /start, /status, /reset 슬래시 커맨드
- 선택지는 버튼으로 표시되고, 버튼이 안 눌리는 환경(모바일 등)을 위해
  '!숫자' 텍스트 입력으로도 같은 선택을 할 수 있게 했습니다.
"""
import discord
from discord import app_commands
from discord.ext import commands

import database
from story_data import STORY, START_NODE


def get_available_choices(node: dict, flags: dict) -> list[dict]:
    """현재 플래그 상태에서 선택 가능한 선택지만 필터링합니다."""
    available = []
    for choice in node["choices"]:
        req = choice.get("requires_flag")
        if req is None:
            available.append(choice)
        else:
            flag_name, flag_value = req
            if flags.get(flag_name) == flag_value:
                available.append(choice)
    return available


def build_embed(node_id: str, node: dict) -> discord.Embed:
    if node["ending"]:
        embed = discord.Embed(
            title=f"🏁 {node['ending']}",
            description=node["text"],
            color=discord.Color.gold(),
        )
    else:
        embed = discord.Embed(
            title="은하철도 노바 익스프레스",
            description=node["text"],
            color=discord.Color.blurple(),
        )
    if node.get("image"):
        embed.set_image(url=node["image"])
    return embed


class ChoiceButton(discord.ui.Button):
    def __init__(self, label: str, index: int, choice: dict, user_id: int):
        super().__init__(
            label=f"{index}. {label}",
            style=discord.ButtonStyle.primary,
            custom_id=f"story_choice:{user_id}:{choice['next']}",
        )
        self.choice = choice
        self.owner_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "본인의 스토리가 아니에요! `/start`로 나만의 이야기를 시작해보세요.",
                ephemeral=True,
            )
            return

        player = await database.get_player(self.owner_id)

        set_flag = self.choice.get("set_flag")
        if set_flag is not None:
            flag_name, flag_value = set_flag
            player["flags"][flag_name] = flag_value

        player["current_node"] = self.choice["next"]
        await database.save_player(player)

        view, embed = await render_node(player)
        await interaction.response.edit_message(embed=embed, view=view)


class StoryView(discord.ui.View):
    def __init__(self, node: dict, available_choices: list[dict], user_id: int):
        super().__init__(timeout=300)
        for i, choice in enumerate(available_choices, start=1):
            self.add_item(ChoiceButton(choice["label"], i, choice, user_id))


async def render_node(player: dict):
    """현재 player 상태를 기반으로 (View, Embed) 튜플을 만듭니다."""
    node_id = player["current_node"]
    node = STORY[node_id]
    available_choices = get_available_choices(node, player["flags"])

    embed = build_embed(node_id, node)

    if node["ending"] or not available_choices:
        view = discord.ui.View()  # 버튼 없음 (엔딩)
        embed.set_footer(text="`/reset`으로 다시 시작할 수 있어요.")
    else:
        view = StoryView(node, available_choices, player["user_id"])
        choice_lines = "\n".join(
            f"**{i}.** {c['label']}" for i, c in enumerate(available_choices, start=1)
        )
        embed.add_field(name="선택지", value=choice_lines, inline=False)
        embed.set_footer(text="버튼을 누르거나, 채팅에 '!1' 처럼 숫자를 입력하세요.")

    return view, embed


class Story(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 유저별로 "마지막으로 보여준 선택지 목록"을 기억해서 텍스트 입력(!1, !2..)을 처리하기 위함
        self.last_choices: dict[int, list[dict]] = {}

    @app_commands.command(name="start", description="스토리를 시작하거나 이어서 진행합니다.")
    async def start(self, interaction: discord.Interaction):
        player = await database.get_player(interaction.user.id)
        view, embed = await render_node(player)

        node = STORY[player["current_node"]]
        available_choices = get_available_choices(node, player["flags"])
        self.last_choices[interaction.user.id] = available_choices

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="status", description="현재 진행 상황을 확인합니다.")
    async def status(self, interaction: discord.Interaction):
        player = await database.get_player(interaction.user.id)
        node = STORY[player["current_node"]]
        title = node["ending"] if node["ending"] else "진행 중"
        embed = discord.Embed(
            title="현재 진행 상황",
            description=f"위치: {title}\n플래그: {player['flags']}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reset", description="스토리를 처음부터 다시 시작합니다.")
    async def reset(self, interaction: discord.Interaction):
        await database.reset_player(interaction.user.id)
        await interaction.response.send_message(
            "진행 상황을 초기화했어요. `/start`로 다시 시작해보세요!", ephemeral=True
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """'!1', '!2' 같은 텍스트 입력으로도 선택할 수 있게 하는 폴백 처리."""
        if message.author.bot:
            return
        content = message.content.strip()
        if not content.startswith("!"):
            return
        number_part = content[1:]
        if not number_part.isdigit():
            return

        user_id = message.author.id
        choices = self.last_choices.get(user_id)
        if not choices:
            return

        idx = int(number_part) - 1
        if idx < 0 or idx >= len(choices):
            await message.channel.send("유효하지 않은 선택지 번호예요.")
            return

        chosen = choices[idx]
        player = await database.get_player(user_id)

        set_flag = chosen.get("set_flag")
        if set_flag is not None:
            flag_name, flag_value = set_flag
            player["flags"][flag_name] = flag_value

        player["current_node"] = chosen["next"]
        await database.save_player(player)

        view, embed = await render_node(player)
        node = STORY[player["current_node"]]
        self.last_choices[user_id] = get_available_choices(node, player["flags"])

        await message.channel.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Story(bot))
