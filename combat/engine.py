"""
전투 엔진.

5x5 그리드 위에서 플레이어(들)와 몬스터가 싸운다.
- 플레이어는 매 라운드 자신의 손패에서 카드 1장을 선택한다.
- 몬스터는 매 라운드 자신의 AI 덱에서 카드 1장을 무작위로 뽑는다.
- 모든 참가자의 카드 initiative(낮은 순)로 정렬해 순서대로 행동을 실행한다.
- 카드의 각 action(move/attack)을 순서대로 처리:
    move  -> 살아있는 가장 가까운 적 쪽으로 최대 value칸 이동 (한 칸씩, 장애물 없음, 다른 유닛이 있는 칸은 통과 불가)
    attack-> 사거리(range) 안에 있는 가장 가까운 적에게 value + 수정자 데미지
"""
import random

from .combat_data import CLASSES, MONSTER_TYPES, new_modifier_deck

GRID_W = 5
GRID_H = 5


def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def pos_label(pos):
    col, row = pos
    return f"{chr(ord('A') + col)}{row + 1}"


class Combatant:
    def __init__(self, cid: str, name: str, team: str, max_hp: int, pos: tuple, emoji: str):
        self.id = cid
        self.name = name
        self.team = team  # "player" or "monster"
        self.max_hp = max_hp
        self.hp = max_hp
        self.pos = pos
        self.emoji = emoji
        self.chosen_card = None  # 이번 라운드에 선택/드로우된 카드
        self.alive = True

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.alive = False


class PlayerCombatant(Combatant):
    def __init__(self, cid: str, name: str, class_key: str, pos: tuple, emoji: str):
        cls = CLASSES[class_key]
        super().__init__(cid, name, "player", cls["max_hp"], pos, emoji)
        self.class_key = class_key
        self.hand = [c["id"] for c in cls["cards"]]  # 남은 손패 (카드 id 목록)
        self.discard = []

    def hand_cards(self):
        cls = CLASSES[self.class_key]
        by_id = {c["id"]: c for c in cls["cards"]}
        return [by_id[cid] for cid in self.hand]

    def play_card(self, card_id: str):
        self.hand.remove(card_id)
        self.discard.append(card_id)
        cls = CLASSES[self.class_key]
        card = next(c for c in cls["cards"] if c["id"] == card_id)
        self.chosen_card = card

    def rest_if_needed(self):
        """손패가 떨어지면 짧은 휴식: 버린 카드를 다시 손으로, 체력 소량 회복."""
        if not self.hand:
            self.hand = self.discard
            self.discard = []
            self.hp = min(self.max_hp, self.hp + 2)
            return True
        return False


class MonsterCombatant(Combatant):
    def __init__(self, cid: str, name: str, type_key: str, pos: tuple, emoji: str):
        mt = MONSTER_TYPES[type_key]
        super().__init__(cid, name, "monster", mt["max_hp"], pos, emoji)
        self.type_key = type_key
        self.ai_deck = list(mt["ai_deck"])
        self.ai_discard = []

    def draw_ai_card(self):
        if not self.ai_deck:
            self.ai_deck, self.ai_discard = self.ai_discard, []
            random.shuffle(self.ai_deck)
        card = self.ai_deck.pop(random.randrange(len(self.ai_deck)))
        self.ai_discard.append(card)
        self.chosen_card = card


class CombatSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.players: dict[int, PlayerCombatant] = {}
        self.monsters: list[MonsterCombatant] = []
        self.round_num = 0
        self.started = False
        self.finished = False
        self.result = None  # "win" / "lose"
        self.modifier_deck = new_modifier_deck()
        self.modifier_discard = []
        self.log = []
        self._next_row = 0
        self._monster_count = {}

    # ---------- 셋업 ----------

    def add_player(self, user_id: int, name: str, class_key: str) -> bool:
        if user_id in self.players or self.started:
            return False
        row = self._next_row % GRID_H
        self._next_row += 1
        emoji = ["🔵", "🟢", "🟣", "🟠", "🟡"][len(self.players) % 5]
        self.players[user_id] = PlayerCombatant(str(user_id), name, class_key, (0, row), emoji)
        return True

    def add_monster(self, type_key: str):
        count = self._monster_count.get(type_key, 0) + 1
        self._monster_count[type_key] = count
        row = (count - 1) % GRID_H
        cid = f"{type_key}_{count}"
        name = f"{MONSTER_TYPES[type_key]['name']} {count}"
        self.monsters.append(MonsterCombatant(cid, name, type_key, (GRID_W - 1, row), "👹"))

    def begin(self) -> bool:
        if self.started or not self.players:
            return False
        self.started = True
        return True

    # ---------- 라운드 진행 ----------

    def alive_players(self):
        return [p for p in self.players.values() if p.alive]

    def alive_monsters(self):
        return [m for m in self.monsters if m.alive]

    def all_players_ready(self) -> bool:
        return all(p.chosen_card is not None for p in self.alive_players())

    def start_new_round(self):
        self.round_num += 1
        self.log = []
        for m in self.alive_monsters():
            m.draw_ai_card()
        for p in self.alive_players():
            p.chosen_card = None

    def submit_player_card(self, user_id: int, card_id: str):
        player = self.players[user_id]
        player.play_card(card_id)

    def draw_modifier(self):
        if not self.modifier_deck:
            self.modifier_deck, self.modifier_discard = self.modifier_discard, []
            random.shuffle(self.modifier_deck)
        mod = self.modifier_deck.pop()
        self.modifier_discard.append(mod)
        return mod  # (label, value)

    def _nearest_enemy(self, actor, enemies):
        alive_enemies = [e for e in enemies if e.alive]
        if not alive_enemies:
            return None
        return min(alive_enemies, key=lambda e: chebyshev(actor.pos, e.pos))

    def _occupied_positions(self, exclude):
        occupied = set()
        for c in list(self.players.values()) + self.monsters:
            if c.alive and c is not exclude:
                occupied.add(c.pos)
        return occupied

    def _move_toward(self, actor, target, steps):
        occupied = self._occupied_positions(actor)
        col, row = actor.pos
        for _ in range(steps):
            tcol, trow = target.pos
            dcol = (tcol > col) - (tcol < col)
            drow = (trow > row) - (trow < row)
            candidates = []
            if dcol != 0 or drow != 0:
                candidates.append((col + dcol, row + drow))
            if dcol != 0:
                candidates.append((col + dcol, row))
            if drow != 0:
                candidates.append((col, row + drow))
            moved = False
            for cand in candidates:
                cc, cr = cand
                if 0 <= cc < GRID_W and 0 <= cr < GRID_H and cand not in occupied:
                    col, row = cand
                    moved = True
                    break
            if not moved:
                break
        actor.pos = (col, row)

    def resolve_round(self):
        """모든 참가자의 카드를 initiative 순으로 실행하고 로그를 남긴다."""
        entries = []
        for p in self.alive_players():
            entries.append((p.chosen_card["initiative"], p, "player"))
        for m in self.alive_monsters():
            entries.append((m.chosen_card["initiative"], m, "monster"))
        entries.sort(key=lambda e: e[0])

        for initiative, actor, team in entries:
            if not actor.alive:
                continue
            enemies = self.monsters if team == "player" else list(self.players.values())
            card = actor.chosen_card
            for action in card["actions"]:
                if not actor.alive:
                    break
                if action["type"] == "move":
                    target = self._nearest_enemy(actor, enemies)
                    if target:
                        before = actor.pos
                        self._move_toward(actor, target, action["value"])
                        if actor.pos != before:
                            self.log.append(
                                f"{actor.emoji}{actor.name}: {pos_label(before)} → {pos_label(actor.pos)} 이동"
                            )
                elif action["type"] == "attack":
                    target = self._nearest_enemy(actor, enemies)
                    if target and chebyshev(actor.pos, target.pos) <= action["range"]:
                        label, mod_value = self.draw_modifier()
                        if mod_value == "miss":
                            self.log.append(f"{actor.emoji}{actor.name}이(가) {target.name}을(를) 공격 → 빗나감(MISS)")
                        else:
                            dmg = action["value"]
                            if mod_value == "x2":
                                dmg *= 2
                            else:
                                dmg = max(0, dmg + mod_value)
                            target.take_damage(dmg)
                            self.log.append(
                                f"{actor.emoji}{actor.name}이(가) {target.name} 공격 (기본 {action['value']} {label}) → {dmg} 데미지 (잔여 HP {target.hp}/{target.max_hp})"
                            )
                            if not target.alive:
                                self.log.append(f"💀 {target.name} 쓰러짐!")

        # 라운드 후처리
        for p in self.alive_players():
            if p.rest_if_needed():
                self.log.append(f"{p.emoji}{p.name}: 손패 소진 → 짧은 휴식 (HP +2, 카드 회수)")

        if not self.alive_monsters():
            self.finished = True
            self.result = "win"
        elif not self.alive_players():
            self.finished = True
            self.result = "lose"

    # ---------- 표시 ----------

    def render_grid(self) -> str:
        cell_map = {}
        for p in self.players.values():
            if p.alive:
                cell_map[p.pos] = p.emoji
        for m in self.monsters:
            if m.alive:
                cell_map[m.pos] = m.emoji

        header = "   " + " ".join(chr(ord('A') + c) for c in range(GRID_W))
        lines = [header]
        for row in range(GRID_H):
            cells = []
            for col in range(GRID_W):
                cells.append(cell_map.get((col, row), "⬜"))
            lines.append(f"{row + 1}  " + " ".join(cells))
        return "```\n" + "\n".join(lines) + "\n```"

    def render_roster(self) -> str:
        lines = []
        for p in self.players.values():
            state = "생존" if p.alive else "쓰러짐"
            lines.append(f"{p.emoji} **{p.name}** ({CLASSES[p.class_key]['name']}) HP {p.hp}/{p.max_hp} [{state}] 위치 {pos_label(p.pos)}")
        for m in self.monsters:
            state = "생존" if m.alive else "처치됨"
            lines.append(f"{m.emoji} {m.name} HP {m.hp}/{m.max_hp} [{state}] 위치 {pos_label(m.pos)}")
        return "\n".join(lines)
