"""
Unit: 캐릭터/몬스터 공통 전투 유닛 클래스.

characters.py 의 create_character() 가 이 클래스를 사용합니다.
지금은 스탯 보유 + 데미지 계산에 필요한 최소한의 기능만 담았고,
SP/기력(에너지) 흐름을 포함한 완전한 턴제 전투 루프는 아직 없습니다.
(Gloomhaven식 그리드 전투 엔진(combat/engine.py)과는 별개의,
붕괴 스타레일 스타일 SP·필살기 전투를 만들고 싶을 때 이 클래스를 확장하면 됩니다.)
"""


class Unit:
    def __init__(self, key: str, name: str, path: str, element: str,
                 max_hp: int, atk: int, defense: int, spd: float,
                 is_enemy: bool = False):
        self.key = key
        self.name = name
        self.path = path
        self.element = element
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.defense = defense
        self.spd = spd
        self.is_enemy = is_enemy

        self.energy = 0
        self.max_energy = 100
        self.sp_contribution = 0  # 필요 시 파티 공용 SP 시스템과 연동
        self.alive = True

    def effective_atk(self) -> float:
        """버프/디버프를 적용한 실질 공격력. 지금은 기본 공격력 그대로 반환."""
        return self.atk

    def gain_energy(self, amount: int):
        self.energy = min(self.max_energy, self.energy + amount)

    def take_damage(self, amount: float):
        self.hp = max(0, self.hp - round(amount))
        if self.hp <= 0:
            self.alive = False

    def heal(self, amount: float):
        self.hp = min(self.max_hp, self.hp + round(amount))

    def __repr__(self):
        return f"<Unit {self.name} HP {self.hp}/{self.max_hp}>"
