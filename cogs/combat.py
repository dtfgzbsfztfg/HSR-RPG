"""
글룸헤이븐 스타일 전투 Cog.

/fight 몬스터종류 [인원수] 로 전투를 시작하면:
1. 참가자들이 버튼으로 직업을 골라 파티에 합류
2. 누군가 "전투 시작"을 누르면 라운드 진행
3. 매 라운드, 각 플레이어가 "카드 선택" 버튼 -> 드롭다운으로 카드 1장 선택
4. 모두 선택하면 이니셔티브 순으로 자동 해결, 결과(그리드+로그) 출력
5. 몬스터 전멸 시 승리, 파티 전멸 시 패배
"""
import discord
from discord import app_commands
from discord.ext import commands

from combat.engine import CombatSession
from combat.combat_data import CLASSES, MONSTER_TYPES

# 채널 id -> CombatSession
active_sessions: dict[int, CombatSession] = {}


def build_lobby_embed(session: CombatSession) -> discord.Embed:
    embed = discord.Embed(
        title="⚔️ 전투 준비",
        description="아래 버튼으로 직업을 선택해 파티에 합류하세요. 준비되면 '전투 시작'을 눌러주세요.",
        color=discord.Color.orange(),
    )
    embed.add_field(name="그리드", value=session.render_grid(), inline=False)
    roster = session.render_roster() or "(아직 아무도 참가하지 않음)"
    embed.add_field(name="참가자", value=roster, inline=False)
    return embed


def build_round_embed(session: CombatSession) -> discord.Embed:
    embed = discord.Embed(
        title=f"🔄 라운드 {session.round_num}",
        description="각자 '카드 선택' 버튼을 눌러 이번 라운드에 쓸 카드를 골라주세요.",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="그리드", value=session.render_grid(), inline=False)
    embed.add_field(name="참가자", value=session.render_roster(), inline=False)
    return embed


def build_result_embed(session: CombatSession) -> discord.Embed:
    color = discord.Color.blurple()
    title = f"📜 라운드 {session.round_num} 결과"
    if session.finished:
        if session.result == "win":
            title = "🎉 전투 승리!"
            color = discord.Color.green()
        else:
            title = "💀 전투 패배..."
            color = discord.Color.red()

    log_text = "\n".join(session.log) if session.log else "(별다른 일이 일어나지 않았다)"
    embed = discord.Embed(title=title, description=log_text, color=color)
    embed.add_field(name="그리드", value=session.render_grid(), inline=False)
    embed.add_field(name="참가자", value=session.render_roster(), inline=False)
    return embed


def card_option_label(card: dict) -> str:
    parts = [f"이니셔티브 {card['initiative']}"]
    for a in card["actions"]:
        if a["type"] == "move":
            parts.append(f"이동{a['value']}")
        else:
            parts.append(f"공격{a['value']}(사거리{a['range']})")
    return " / ".join(parts)


class CardSelect(discord.ui.Select):
    def __init__(self, session: CombatSession, user_id: int):
        self.session = session
        self.owner_id = user_id
        player = session.players[user_id]
        options = [
            discord.SelectOption(label=card["id"], description=card_option_label(card))
            for card in player.hand_cards()
        ]
        super().__init__(placeholder="이번 라운드에 쓸 카드를 고르세요", options=options)

    async def callback(self, interaction: discord.Interaction):
        card_id = self.values[0]
        self.session.submit_player_card(self.owner_id, card_id)
        await interaction.response.edit_message(
            content=f"✅ `{card_id}` 카드를 선택했어요.", view=None
        )

        if self.session.all_players_ready():
            self.session.resolve_round()
            result_embed = build_result_embed(self.session)
            await interaction.channel.send(embed=result_embed)

            if not self.session.finished:
                self.session.start_new_round()
                round_embed = build_round_embed(self.session)
                await interaction.channel.send(embed=round_embed, view=CardPromptView(self.session))
            else:
                active_sessions.pop(self.session.channel_id, None)


class CardSelectPromptView(discord.ui.View):
    def __init__(self, session: CombatSession, user_id: int):
        super().__init__(timeout=180)
        self.add_item(CardSelect(session, user_id))


class CardPromptView(discord.ui.View):
    """매 라운드마다 채널에 붙는, '카드 선택' 버튼 하나짜리 뷰."""

    def __init__(self, session: CombatSession):
        super().__init__(timeout=600)
        self.session = session

    @discord.ui.button(label="카드 선택", style=discord.ButtonStyle.primary)
    async def choose_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = self.session
        if interaction.user.id not in session.players:
            await interaction.response.send_message("전투에 참가하지 않으셨어요.", ephemeral=True)
            return
        player = session.players[interaction.user.id]
        if not player.alive:
            await interaction.response.send_message("이미 쓰러져서 이번 전투에 행동할 수 없어요.", ephemeral=True)
            return
        if player.chosen_card is not None:
            await interaction.response.send_message("이미 이번 라운드 카드를 선택했어요.", ephemeral=True)
            return

        view = CardSelectPromptView(session, interaction.user.id)
        await interaction.response.send_message("카드를 선택하세요:", view=view, ephemeral=True)


class LobbyView(discord.ui.View):
    def __init__(self, session: CombatSession):
        super().__init__(timeout=600)
        self.session = session

    async def _join(self, interaction: discord.Interaction, class_key: str):
        session = self.session
        if session.started:
            await interaction.response.send_message("이미 전투가 시작되었어요.", ephemeral=True)
            return
        ok = session.add_player(interaction.user.id, interaction.user.display_name, class_key)
        if not ok:
            await interaction.response.send_message("이미 참가했어요.", ephemeral=True)
            return
        await interaction.response.edit_message(embed=build_lobby_embed(session), view=self)

    @discord.ui.button(label="돌격병으로 참가", style=discord.ButtonStyle.danger)
    async def join_warrior(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._join(interaction, "돌격병")

    @discord.ui.button(label="저격수로 참가", style=discord.ButtonStyle.success)
    async def join_sniper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._join(interaction, "저격수")

    @discord.ui.button(label="전투 시작", style=discord.ButtonStyle.primary)
    async def start_fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = self.session
        if not session.begin():
            await interaction.response.send_message(
                "아직 아무도 참가하지 않았거나 이미 시작됐어요.", ephemeral=True
            )
            return
        session.start_new_round()
        await interaction.response.edit_message(embed=build_lobby_embed(session), view=None)
        await interaction.channel.send(embed=build_round_embed(session), view=CardPromptView(session))


class Combat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="fight", description="글룸헤이븐 스타일 전투를 시작합니다.")
    @app_commands.choices(
        monster=[
            app_commands.Choice(name=key, value=key) for key in MONSTER_TYPES.keys()
        ]
    )
    async def fight(
        self,
        interaction: discord.Interaction,
        monster: app_commands.Choice[str],
        count: int = 1,
    ):
        channel_id = interaction.channel_id
        if channel_id in active_sessions and not active_sessions[channel_id].finished:
            await interaction.response.send_message(
                "이 채널에 이미 진행 중인 전투가 있어요. 끝날 때까지 기다려주세요.",
                ephemeral=True,
            )
            return

        count = max(1, min(count, 5))
        session = CombatSession(channel_id)
        for _ in range(count):
            session.add_monster(monster.value)
        active_sessions[channel_id] = session

        await interaction.response.send_message(embed=build_lobby_embed(session), view=LobbyView(session))

    @app_commands.command(name="fight_classes", description="전투 직업 목록과 설명을 봅니다.")
    async def fight_classes(self, interaction: discord.Interaction):
        embed = discord.Embed(title="직업 목록", color=discord.Color.blurple())
        for key, cls in CLASSES.items():
            embed.add_field(name=f"{key} (HP {cls['max_hp']})", value=cls["desc"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Combat(bot))
