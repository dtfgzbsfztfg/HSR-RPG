"""
글룸헤이븐 스타일 전투 데이터.

- CLASSES: 플레이어 직업별 카드 덱. 각 카드는 initiative(이니셔티브,
  낮을수록 먼저 행동) + actions(순서대로 실행되는 행동 목록)를 가짐.
- MONSTER_TYPES: 몬스터 스탯 + AI 카드 덱(플레이어 카드와 동일한 구조).
- MODIFIER_DECK: 공격 시 뽑는 수정자 카드 (글룸헤이븐의 어택 모디파이어 덱 오마주).

action 종류:
  {"type": "move", "value": N}                 -> 가장 가까운 적 방향으로 최대 N칸 이동
  {"type": "attack", "value": N, "range": R}    -> 사거리 R 이내 가장 가까운 적을 N 데미지로 공격
"""
import random

MODIFIER_DECK_TEMPLATE = [
    ("+0", 0), ("+0", 0),
    ("+1", 1), ("+1", 1),
    ("+2", 2),
    ("-1", -1), ("-1", -1),
    ("-2", -2),
    ("x2", "x2"),   # 데미지 2배
    ("MISS", "miss"),  # 완전 빗나감
]


def new_modifier_deck() -> list:
    deck = list(MODIFIER_DECK_TEMPLATE)
    random.shuffle(deck)
    return deck


CLASSES = {
    "돌격병": {
        "name": "돌격병",
        "desc": "근접 탱커. 체력이 높고 적에게 붙어 싸운다.",
        "max_hp": 12,
        "cards": [
            {"id": "돌격_01", "initiative": 15, "actions": [
                {"type": "move", "value": 2}, {"type": "attack", "value": 3, "range": 1}]},
            {"id": "돌격_02", "initiative": 32, "actions": [
                {"type": "attack", "value": 4, "range": 1}, {"type": "move", "value": 1}]},
            {"id": "돌격_03", "initiative": 48, "actions": [
                {"type": "move", "value": 3}, {"type": "attack", "value": 2, "range": 1}]},
            {"id": "돌격_04", "initiative": 61, "actions": [
                {"type": "attack", "value": 5, "range": 1}]},
            {"id": "돌격_05", "initiative": 74, "actions": [
                {"type": "move", "value": 4}]},
            {"id": "돌격_06", "initiative": 20, "actions": [
                {"type": "attack", "value": 3, "range": 1}, {"type": "attack", "value": 2, "range": 1}]},
        ],
    },
    "저격수": {
        "name": "저격수",
        "desc": "원거리 딜러. 체력은 낮지만 멀리서 공격한다.",
        "max_hp": 8,
        "cards": [
            {"id": "저격_01", "initiative": 25, "actions": [
                {"type": "move", "value": 1}, {"type": "attack", "value": 3, "range": 3}]},
            {"id": "저격_02", "initiative": 40, "actions": [
                {"type": "attack", "value": 4, "range": 3}]},
            {"id": "저격_03", "initiative": 55, "actions": [
                {"type": "move", "value": 2}, {"type": "attack", "value": 2, "range": 3}]},
            {"id": "저격_04", "initiative": 68, "actions": [
                {"type": "attack", "value": 2, "range": 4}, {"type": "move", "value": 1}]},
            {"id": "저격_05", "initiative": 10, "actions": [
                {"type": "move", "value": 3}]},
            {"id": "저격_06", "initiative": 80, "actions": [
                {"type": "attack", "value": 5, "range": 2}]},
        ],
    },
}

MONSTER_TYPES = {
    "우주해적": {
        "name": "우주해적",
        "max_hp": 8,
        "ai_deck": [
            {"initiative": 30, "actions": [
                {"type": "move", "value": 2}, {"type": "attack", "value": 2, "range": 1}]},
            {"initiative": 55, "actions": [
                {"type": "attack", "value": 3, "range": 1}]},
            {"initiative": 20, "actions": [
                {"type": "move", "value": 3}, {"type": "attack", "value": 1, "range": 1}]},
            {"initiative": 70, "actions": [
                {"type": "move", "value": 1}, {"type": "attack", "value": 2, "range": 1}]},
        ],
    },
    "정찰드론": {
        "name": "정찰드론",
        "max_hp": 5,
        "ai_deck": [
            {"initiative": 35, "actions": [
                {"type": "move", "value": 1}, {"type": "attack", "value": 2, "range": 3}]},
            {"initiative": 60, "actions": [
                {"type": "attack", "value": 1, "range": 4}]},
            {"initiative": 15, "actions": [
                {"type": "move", "value": 2}]},
            {"initiative": 45, "actions": [
                {"type": "attack", "value": 2, "range": 3}]},
        ],
    },
}
