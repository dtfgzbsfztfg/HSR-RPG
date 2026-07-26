"""
플레이어블 캐릭터 데이터.
붕괴 스타레일 원작의 컨셉(운명/속성/역할)을 참고한 비상업적 팬 게임용 스탯입니다.
실제 게임 수치와는 다르며, 자체 밸런스로 단순화했습니다.

각 캐릭터는 다음 3가지 행동을 가집니다:
  - basic:     기본 공격. SP(스킬 포인트) +1, 에너지 획득.
  - skill:     전투 스킬. SP -1 소모, 에너지 획득.
  - ultimate:  필살기. 에너지 100 소모, 강력한 효과.
"""

from .unit import Unit

CHARACTER_TEMPLATES = {
    "march7th": {
        "name": "Mar. 7th",
        "path": "preservation",
        "element": "ice",
        "max_hp": 1100, "atk": 550, "defense": 700, "spd": 102,
        "desc": "아군을 보호막으로 지키는 수호자",
        "rarity": 4,
    },
    "danheng": {
        "name": "단항",
        "path": "hunt",
        "element": "wind",
        "max_hp": 950, "atk": 750, "defense": 500, "spd": 110,
        "desc": "단일 대상에게 강력한 피해를 입히는 추적자",
        "rarity": 4,
    },
    "asta": {
        "name": "아스타",
        "path": "harmony",
        "element": "fire",
        "max_hp": 900, "atk": 500, "defense": 480, "spd": 100,
        "desc": "아군 전체의 속도와 공격력을 올리는 천문학자",
        "rarity": 4,
    },
    "natasha": {
        "name": "나타샤",
        "path": "abundance",
        "element": "physical",
        "max_hp": 1050, "atk": 480, "defense": 520, "spd": 98,
        "desc": "아군을 치유하는 의사",
        "rarity": 4,
    },
    "sampo": {
        "name": "삼포",
        "path": "nihility",
        "element": "wind",
        "max_hp": 980, "atk": 520, "defense": 500, "spd": 104,
        "desc": "지속 피해와 방어 감소로 적을 약화시키는 상인",
        "rarity": 4,
    },
    "herta": {
        "name": "헤르타",
        "path": "erudition",
        "element": "ice",
        "max_hp": 920, "atk": 700, "defense": 460, "spd": 96,
        "desc": "적 전체에게 광역 피해를 입히는 천재 소녀",
        "rarity": 4,
    },
}

# 스킬 정의: 각 함수는 (actor, targets, allies, enemies, log) -> None 형태의 효과 함수
# dmg_mult 는 actor.effective_atk() 에 곱해지는 배율입니다.

SKILLS = {
    "march7th": {
        "basic": {"name": "장총 사격", "dmg_mult": 1.0, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "얼음 방패", "target": "single_ally", "sp_cost": 1, "energy_gain": 30,
                  "shield_ratio": 0.25},
        "ultimate": {"name": "동결의 맹세", "target": "all_allies", "energy_cost": 100,
                     "shield_ratio": 0.20},
    },
    "danheng": {
        "basic": {"name": "창격", "dmg_mult": 1.0, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "선풍 관통", "dmg_mult": 1.8, "target": "single_enemy", "sp_cost": 1,
                  "energy_gain": 30},
        "ultimate": {"name": "구천십지", "dmg_mult": 3.2, "target": "single_enemy", "energy_cost": 100},
    },
    "asta": {
        "basic": {"name": "화염탄", "dmg_mult": 0.9, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "관측 지원", "target": "all_allies", "sp_cost": 1, "energy_gain": 30,
                  "spd_buff": 0.20, "duration": 3},
        "ultimate": {"name": "초신성 강림", "target": "all_allies", "energy_cost": 100,
                     "atk_buff": 0.30, "duration": 3},
    },
    "natasha": {
        "basic": {"name": "약침 던지기", "dmg_mult": 0.8, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "치료의 손길", "target": "single_ally", "sp_cost": 1, "energy_gain": 30,
                  "heal_ratio": 0.25},
        "ultimate": {"name": "생명의 파동", "target": "all_allies", "energy_cost": 100,
                     "heal_ratio": 0.30},
    },
    "sampo": {
        "basic": {"name": "폭탄 투척", "dmg_mult": 0.9, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "윈드슬래시 부비트랩", "dmg_mult": 0.6, "target": "single_enemy", "sp_cost": 1,
                  "energy_gain": 30, "dot_ratio": 0.35, "duration": 3, "def_down": 0.15},
        "ultimate": {"name": "대폭발", "dmg_mult": 1.5, "target": "all_enemies", "energy_cost": 100,
                     "dot_ratio": 0.4, "duration": 2},
    },
    "herta": {
        "basic": {"name": "얼음 파편", "dmg_mult": 0.7, "target": "single_enemy", "energy_gain": 20},
        "skill": {"name": "냉기 폭발", "dmg_mult": 1.3, "target": "all_enemies", "sp_cost": 1,
                  "energy_gain": 30},
        "ultimate": {"name": "절대영도", "dmg_mult": 2.6, "target": "all_enemies", "energy_cost": 100},
    },
}


def create_character(key: str) -> Unit:
    t = CHARACTER_TEMPLATES[key]
    return Unit(
        key=key, name=t["name"], path=t["path"], element=t["element"],
        max_hp=t["max_hp"], atk=t["atk"], defense=t["defense"], spd=t["spd"],
        is_enemy=False,
    )


def list_characters():
    return list(CHARACTER_TEMPLATES.keys())


# =====================================================================
# 전체 로스터 자동 생성 시스템
# ---------------------------------------------------------------------
# 90여 명에 달하는 붕괴 스타레일 전체 플레이어블 캐릭터를 전부 손으로
# 하나하나 튜닝하는 대신, "운명(Path)별 스킬 틀"에 캐릭터의 이름/속성/
# 희귀도만 끼워 넣는 방식으로 자동 생성합니다.
#   - 위에 있는 6명(마치7사, 단항, 아스타, 나타샤, 삼포, 헤르타)은 기존처럼
#     수동으로 세밀하게 튜닝된 스킬을 그대로 사용합니다.
#   - 아래 ROSTER_EXTRA 목록의 캐릭터들은 같은 운명을 가진 캐릭터라면
#     비슷한 스킬 구조(예: 사냥=단일 대상 버스트, 조화=아군 버프)를 공유하되,
#     이름/속성에 따라 수치가 조금씩 달라집니다.
# =====================================================================
import hashlib


PATH_ARCHETYPE = {
    "destruction":  dict(hp=1.05, atk=1.00, defn=0.95, spd=1.00),
    "hunt":         dict(hp=0.90, atk=1.05, defn=0.85, spd=1.12),
    "erudition":    dict(hp=0.90, atk=1.08, defn=0.80, spd=0.96),
    "harmony":      dict(hp=0.95, atk=0.85, defn=0.90, spd=1.00),
    "preservation": dict(hp=1.25, atk=0.80, defn=1.30, spd=0.95),
    "abundance":    dict(hp=1.05, atk=0.80, defn=1.00, spd=0.96),
    "nihility":     dict(hp=0.95, atk=0.95, defn=0.85, spd=1.02),
    "remembrance":  dict(hp=1.10, atk=0.95, defn=1.00, spd=0.96),
    "elation":      dict(hp=0.90, atk=1.05, defn=0.85, spd=1.10),
}

BASE_STATS_BY_RARITY = {
    5: dict(hp=1000, atk=620, defn=480, spd=100),
    4: dict(hp=850, atk=500, defn=430, spd=96),
}

# 붕괴 스타레일 전체 캐릭터 로스터 (2026년 7월 기준, 4.4 버전 예고 캐릭터 제외).
# 형식: (내부 key, 표시 이름, 운명, 속성, 희귀도)
# march7th/danheng/asta/natasha/sampo/herta 는 위에서 이미 수동 정의했으므로 여기서는 제외합니다.
ROSTER_EXTRA = [
    # --- 남성 캐릭터 ---
    ("ashveil", "애쉬베일", "hunt", "lightning", 5),
    ("danheng_permansor", "단항·등황", "preservation", "physical", 5),  # 실제 속성: 물리 (원본은 imaginary로 잘못 적혀 있었음)
    ("archer", "아처", "hunt", "quantum", 5),
    ("phainon", "파이논", "destruction", "physical", 5),
    ("anaxa", "아낙사", "erudition", "wind", 5),
    ("mydei", "마이데이", "destruction", "imaginary", 5),
    ("sunday", "선데이", "harmony", "imaginary", 5),
    ("jiaoqiu", "초구", "nihility", "fire", 5),
    ("moze", "맥택", "hunt", "lightning", 4),
    ("boothill", "부트힐", "hunt", "physical", 5),
    ("aventurine", "어벤츄린", "preservation", "imaginary", 5),
    ("gallagher", "갤러거", "abundance", "fire", 4),
    ("misha", "미샤", "destruction", "ice", 4),
    ("drratio", "Dr. 레이시오", "hunt", "imaginary", 5),
    ("argenti", "아젠티", "erudition", "physical", 5),
    ("danheng_il", "단항·음월", "destruction", "imaginary", 5),
    ("luka", "루카", "nihility", "physical", 4),
    ("blade", "블레이드", "destruction", "wind", 5),
    ("luocha", "나찰", "abundance", "imaginary", 5),
    ("jingyuan", "경원", "erudition", "lightning", 5),
    ("welt", "웰트", "nihility", "imaginary", 5),
    ("gepard", "게파드", "preservation", "ice", 5),
    ("yanqing", "연경", "hunt", "ice", 5),
    ("arlan", "아를란", "destruction", "lightning", 4),
    ("mortenax_blade", "천야·블레이드", "nihility", "fire", 5),  # 실제 운명의 길: 2026년 신설된 "공허(Void)". 엔진에 아직 없어 nihility로 근사
    # --- 여성/기타 캐릭터 ---
    ("silverwolf999", "은랑 LV.999", "elation", "imaginary", 5),
    ("evanescia", "에바네시아", "elation", "physical", 5),
    ("elation_tb", "개척자(환락)", "elation", "lightning", 5),
    ("sparxie", "스파키", "elation", "fire", 5),
    ("yaoguang", "효광", "elation", "physical", 5),
    ("dahlia", "달리아", "nihility", "fire", 5),
    ("cyrene", "키레네", "remembrance", "ice", 5),
    ("evernight", "에버나이트", "remembrance", "ice", 5),
    ("cerydra", "케리드라", "harmony", "wind", 5),
    ("hysilens", "히실렌스", "nihility", "physical", 5),
    ("saber", "세이버", "destruction", "wind", 5),
    ("cipher", "사이퍼", "nihility", "quantum", 5),
    ("hyacine", "히아킨", "remembrance", "wind", 5),
    ("castorice", "카스토리스", "remembrance", "quantum", 5),
    ("tribbie", "트리비", "harmony", "quantum", 5),
    ("aglaea", "아글라이아", "remembrance", "lightning", 5),
    ("remembrance_tb", "개척자(기억)", "remembrance", "ice", 5),
    ("theherta", "더 헤르타", "erudition", "ice", 5),
    ("fugue", "망귀인", "nihility", "fire", 5),
    ("rappa", "라파", "erudition", "imaginary", 5),
    ("lingsha", "영사", "abundance", "fire", 5),
    ("feixiao", "비소", "hunt", "wind", 5),
    ("yunli", "운리", "destruction", "physical", 5),
    ("hunt_march7th", "Mar. 7th·수렵", "hunt", "imaginary", 4),
    ("jade", "제이드", "erudition", "quantum", 5),
    ("firefly", "반디", "destruction", "fire", 5),
    ("harmony_tb", "개척자(조화)", "harmony", "imaginary", 5),
    ("robin", "로빈", "harmony", "physical", 5),
    ("acheron", "아케론", "nihility", "lightning", 5),
    ("sparkle", "스파클", "harmony", "quantum", 5),
    ("blackswan", "블랙 스완", "nihility", "wind", 5),
    ("ruanmei", "완·매", "harmony", "ice", 5),
    ("xueyi", "설의", "destruction", "quantum", 4),
    ("hanya", "한아", "harmony", "physical", 4),
    ("huohuo", "곽향", "abundance", "wind", 5),
    ("topaznumby", "토파즈&복순이", "hunt", "fire", 5),
    ("guinaifen", "계네빈", "nihility", "fire", 4),
    ("jingliu", "경류", "destruction", "ice", 5),
    ("fuxuan", "부현", "preservation", "quantum", 5),
    ("lynx", "링스", "abundance", "quantum", 4),
    ("kafka", "카프카", "nihility", "lightning", 5),
    ("yukong", "어공", "harmony", "imaginary", 4),
    ("silverwolf", "은랑", "nihility", "quantum", 5),
    ("seele", "제레", "hunt", "quantum", 5),
    ("himeko", "히메코", "erudition", "fire", 5),
    ("preservation_tb", "개척자(보존)", "preservation", "fire", 5),
    ("clara", "클라라", "destruction", "physical", 5),
    ("bailu", "백로", "abundance", "lightning", 5),
    ("bronya", "브로냐", "harmony", "wind", 5),
    ("destruction_tb", "개척자(파멸)", "destruction", "physical", 5),
    ("pela", "페라", "nihility", "ice", 4),
    ("hook", "후크", "destruction", "fire", 4),
    ("qingque", "청작", "erudition", "quantum", 4),
    ("serval", "서벌", "erudition", "lightning", 4),
    ("tingyun", "정운", "harmony", "lightning", 4),
    ("sushang", "소상", "hunt", "physical", 4),
    # --- 4.4 버전 신규 / 콜라보 캐릭터 ---
    ("himeko_nova", "히메코·노바", "erudition", "fire", 5),
    ("gilgamesh", "길가메시", "destruction", "lightning", 5),
    ("tohsaka_rin", "토오사카 린", "erudition", "quantum", 5),
]


def _name_seed(name: str) -> int:
    return int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)


def _variance(seed: int, shift: int, spread: float = 1.0) -> float:
    """이름을 시드로 한 -10%~+10% 범위의 결정론적(항상 같은 값) 편차."""
    bucket = (seed >> shift) % 21  # 0~20
    return 1 + ((bucket - 10) / 100) * spread


def _generate_stats(name: str, path: str, rarity: int):
    base = BASE_STATS_BY_RARITY[rarity]
    arche = PATH_ARCHETYPE[path]
    seed = _name_seed(name)
    hp = int(base["hp"] * arche["hp"] * _variance(seed, 0))
    atk = int(base["atk"] * arche["atk"] * _variance(seed, 8))
    defn = int(base["defn"] * arche["defn"] * _variance(seed, 16))
    spd = round(base["spd"] * arche["spd"] * _variance(seed, 24, spread=0.6), 1)
    return hp, atk, defn, spd


ELEMENT_ENEMY_EFFECT = {
    # 적 대상 스킬에 붙는 속성별 부가 효과 (원작 원소 상성 컨셉을 단순화)
    "ice": {"spd_down": 0.15},
    "wind": {"dot_ratio": 0.18},
    "quantum": {"def_down": 0.12},
    "fire": {"dot_ratio": 0.22},
    # lightning/physical/imaginary 는 부가효과 없이 순수 수치로 차별화
}


def _make_skills(name: str, path: str, element: str):
    enemy_extra = ELEMENT_ENEMY_EFFECT.get(element, {})

    if path == "destruction":
        return {
            "basic": {"name": f"{name}의 일격", "dmg_mult": 1.0, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 파쇄격", "dmg_mult": 1.7, "target": "single_enemy", "sp_cost": 1,
                      "energy_gain": 30, **enemy_extra, "duration": 2},
            "ultimate": {"name": f"{name}의 전장 강타", "dmg_mult": 1.6, "target": "all_enemies", "energy_cost": 100},
        }
    if path == "hunt":
        return {
            "basic": {"name": f"{name}의 속사", "dmg_mult": 1.0, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 필중격", "dmg_mult": 2.1, "target": "single_enemy", "sp_cost": 1,
                      "energy_gain": 30, **enemy_extra, "duration": 2},
            "ultimate": {"name": f"{name}의 종언의 일격", "dmg_mult": 3.4, "target": "single_enemy", "energy_cost": 100},
        }
    if path == "erudition":
        return {
            "basic": {"name": f"{name}의 파편탄", "dmg_mult": 0.7, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 광역 폭격", "dmg_mult": 1.3, "target": "all_enemies", "sp_cost": 1,
                      "energy_gain": 30, **enemy_extra, "duration": 2},
            "ultimate": {"name": f"{name}의 절멸 진리", "dmg_mult": 2.7, "target": "all_enemies", "energy_cost": 100},
        }
    if path == "harmony":
        return {
            "basic": {"name": f"{name}의 견제 사격", "dmg_mult": 0.8, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 지원 신호", "target": "all_allies", "sp_cost": 1, "energy_gain": 30,
                      "atk_buff": 0.20, "duration": 3},
            "ultimate": {"name": f"{name}의 축복", "target": "all_allies", "energy_cost": 100,
                         "atk_buff": 0.30, "spd_buff": 0.15, "duration": 3},
        }
    if path == "preservation":
        return {
            "basic": {"name": f"{name}의 방어 반격", "dmg_mult": 0.9, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 수호 방벽", "target": "single_ally", "sp_cost": 1, "energy_gain": 30,
                      "shield_ratio": 0.28},
            "ultimate": {"name": f"{name}의 절대 방어", "target": "all_allies", "energy_cost": 100,
                         "shield_ratio": 0.22},
        }
    if path == "abundance":
        return {
            "basic": {"name": f"{name}의 응급 처치", "dmg_mult": 0.7, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 치유술", "target": "single_ally", "sp_cost": 1, "energy_gain": 30,
                      "heal_ratio": 0.28},
            "ultimate": {"name": f"{name}의 생명의 축복", "target": "all_allies", "energy_cost": 100,
                         "heal_ratio": 0.32},
        }
    if path == "nihility":
        return {
            "basic": {"name": f"{name}의 저격", "dmg_mult": 0.8, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 저주", "dmg_mult": 0.5, "target": "single_enemy", "sp_cost": 1,
                      "energy_gain": 30, "dot_ratio": 0.3, "def_down": 0.15, "duration": 3},
            "ultimate": {"name": f"{name}의 파멸의 낙인", "dmg_mult": 1.2, "target": "all_enemies",
                         "energy_cost": 100, "dot_ratio": 0.35, "duration": 2},
        }
    if path == "remembrance":
        return {
            "basic": {"name": f"{name}의 기억 조각", "dmg_mult": 0.8, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 잔향", "target": "single_ally", "sp_cost": 1, "energy_gain": 30,
                      "heal_ratio": 0.15, "shield_ratio": 0.12},
            "ultimate": {"name": f"{name}의 영원한 순간", "dmg_mult": 2.2, "target": "all_enemies",
                         "energy_cost": 100, **enemy_extra, "duration": 2},
        }
    if path == "elation":
        return {
            "basic": {"name": f"{name}의 쾌속 일격", "dmg_mult": 1.0, "target": "single_enemy", "energy_gain": 20},
            "skill": {"name": f"{name}의 광란 연격", "dmg_mult": 1.9, "target": "single_enemy", "sp_cost": 1,
                      "energy_gain": 30, **enemy_extra, "duration": 2},
            "ultimate": {"name": f"{name}의 폭주", "dmg_mult": 3.1, "target": "single_enemy", "energy_cost": 100},
        }
    raise ValueError(f"알 수 없는 운명: {path}")


def _register_full_roster():
    for key, name, path, element, rarity in ROSTER_EXTRA:
        if key in CHARACTER_TEMPLATES:
            continue  # 이미 수동으로 정의된 캐릭터는 건드리지 않음
        hp, atk, defn, spd = _generate_stats(name, path, rarity)
        CHARACTER_TEMPLATES[key] = {
            "name": name, "path": path, "element": element,
            "max_hp": hp, "atk": atk, "defense": defn, "spd": spd,
            "desc": f"{PATH_KOR.get(path, path)} · {ELEMENT_KOR.get(element, element)} 속성 ({rarity}성)",
            "rarity": rarity,
        }
        SKILLS[key] = _make_skills(name, path, element)


PATH_KOR = {
    "destruction": "파멸", "hunt": "사냥", "erudition": "지식", "harmony": "조화",
    "preservation": "보존", "abundance": "풍요", "nihility": "허무",
    "remembrance": "기억", "elation": "환락",
}
ELEMENT_KOR = {
    "physical": "물리", "fire": "화", "ice": "빙", "lightning": "뇌",
    "wind": "풍", "quantum": "양자", "imaginary": "허수",
}

_register_full_roster()


# =====================================================================
# 실제 필살기(Ultimate) 데이터 반영
# ---------------------------------------------------------------------
# 붕괴 스타레일 위키(Fandom)의 "Ultimate" 문서 및 각 캐릭터별 빌드 가이드에서
# 확인한 실제 필살기 배율/효과를 바탕으로, 위에서 자동 생성된 필살기를
# 캐릭터별로 덮어씁니다. (기본공격/스킬은 기존 운명별 템플릿 그대로 유지)
# 수치는 Lv.80 기준 최소치(추가 어웨이크닝 미적용)를 기준으로 단순화했고,
# 우리 엔진이 지원하는 효과(단일/광역 피해, 지속피해, 방어/속도 감소, 보호막,
# 회복, 공격력/속도 버프)에 맞춰 근사치로 변환했습니다.
# 정확한 필살기 명칭이 확인되지 않은 극히 일부 캐릭터는 운명에 맞는
# 설명형 이름을 그대로 사용했습니다.
# =====================================================================

REAL_ULTIMATES = {
    # --- 수동 정의 6명 보정 ---
    "march7th": {  # 실제로는 보호막이 아니라 광역 빙속성 피해 + 빙결
        "name": "설색 광상곡", "dmg_mult": 0.9, "target": "all_enemies",
        "energy_cost": 120, "spd_down": 0.3, "duration": 1,
    },
    "danheng": {
        "name": "천리 참격", "dmg_mult": 2.4, "target": "single_enemy", "energy_cost": 100,
    },
    "asta": {  # 실제로는 공격력이 아니라 아군 전체 속도 버프
        "name": "초신성", "target": "all_allies", "energy_cost": 120,
        "spd_buff": 0.20, "duration": 2,
    },
    "natasha": {
        "name": "인애의 기도", "target": "all_allies", "energy_cost": 90, "heal_ratio": 0.14,
    },
    "sampo": {
        "name": "질풍노도", "dmg_mult": 0.96, "target": "all_enemies", "energy_cost": 120,
        "dot_ratio": 0.25, "duration": 2,
    },
    "herta": {
        "name": "절대영도", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 110,
    },

    # --- 자동생성 캐릭터 실제 필살기로 교체 ---
    "danheng_permansor": {"name": "혼룡 현신", "dmg_mult": 1.5, "target": "all_enemies", "energy_cost": 135},
    "qingque": {"name": "천기묘산", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 140},
    "harmony_tb": {"name": "백업 댄서", "target": "all_allies", "energy_cost": 140, "atk_buff": 0.20, "duration": 3},
    "yanqing": {"name": "소울스틸 싱크로율 100%", "dmg_mult": 2.1, "target": "single_enemy", "energy_cost": 140},
    "tingyun": {"name": "축복의 인도", "target": "single_ally", "energy_cost": 130, "atk_buff": 0.20, "duration": 2},
    "danheng_il": {"name": "웅혼일소", "dmg_mult": 1.8, "target": "single_enemy", "energy_cost": 140},
    "blackswan": {"name": "계시", "dmg_mult": 0.72, "target": "all_enemies", "energy_cost": 120, "def_down": 0.15, "duration": 2},
    "destruction_tb": {"name": "결별의 일격", "dmg_mult": 3.0, "target": "single_enemy", "energy_cost": 130},
    "feixiao": {"name": "천리 추종", "dmg_mult": 3.8, "target": "single_enemy", "energy_cost": 110},
    "hook": {"name": "타오르는 불장난", "dmg_mult": 2.4, "target": "single_enemy", "energy_cost": 120},
    "seele": {"name": "버터플라이 이레이저", "dmg_mult": 2.55, "target": "single_enemy", "energy_cost": 120},
    "gallagher": {"name": "취기 만연", "dmg_mult": 0.75, "target": "all_enemies", "energy_cost": 110},
    "luka": {"name": "격투 의지", "dmg_mult": 1.98, "target": "single_enemy", "energy_cost": 130},
    "aglaea": {"name": "지고의 자태", "target": "single_ally", "energy_cost": 350, "atk_buff": 0.30, "spd_buff": 0.15, "duration": 3},
    "moze": {"name": "전격 추적", "dmg_mult": 1.62, "target": "single_enemy", "energy_cost": 120},
    "blade": {"name": "검은 홀로 서다", "dmg_mult": 1.8, "target": "single_enemy", "energy_cost": 130},
    "luocha": {"name": "삶과 죽음의 경계", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 100},
    "xueyi": {"name": "겁괴의 저울", "dmg_mult": 1.5, "target": "single_enemy", "energy_cost": 120},
    "yukong": {"name": "울리는 활시위", "dmg_mult": 2.28, "target": "single_enemy", "energy_cost": 130},
    "castorice": {"name": "새싹의 한계", "target": "single_ally", "energy_cost": 200, "summon": True,
                  "atk_buff": 0.20, "duration": 3},
    "lingsha": {"name": "미몽의 안개", "target": "all_allies", "energy_cost": 110, "heal_ratio": 0.28},
    "boothill": {"name": "정오의 결투", "dmg_mult": 2.4, "target": "single_enemy", "energy_cost": 115, "spd_down": 0.3, "duration": 2},
    "yunli": {"name": "천단, 파쇄의 혼", "dmg_mult": 2.6, "target": "single_enemy", "energy_cost": 120},
    "gepard": {"name": "결의의 얼음벽", "target": "all_allies", "energy_cost": 100, "shield_ratio": 0.28},
    "saber": {"name": "황금 왕의 검", "dmg_mult": 1.6, "target": "all_enemies", "energy_cost": 360},
    "bailu": {"name": "행운의 부적", "target": "all_allies", "energy_cost": 100, "heal_ratio": 0.12},
    "jingliu": {"name": "월파 참월살", "dmg_mult": 1.8, "target": "single_enemy", "energy_cost": 140},
    "argenti": {"name": "이 정원에서, 지고한 아름다움이 내리다", "dmg_mult": 1.0, "target": "all_enemies", "energy_cost": 90},
    "arlan": {"name": "감전의 낙뢰", "dmg_mult": 1.92, "target": "single_enemy", "energy_cost": 110},
    "firefly": {"name": "완전연소", "target": "single_ally", "energy_cost": 240, "transform": True,
                "atk_buff": 0.30, "spd_buff": 0.15, "duration": 2},
    "phainon": {"name": "카슬라나 강림", "dmg_mult": 4.8, "target": "all_enemies", "energy_cost": 120},
    "himeko": {"name": "폭염어천가", "dmg_mult": 1.38, "target": "all_enemies", "energy_cost": 120},
    "serval": {"name": "락 유 투나잇", "dmg_mult": 1.08, "target": "all_enemies", "energy_cost": 100},
    "jingyuan": {"name": "뇌정지주 강림", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 130},
    "hysilens": {"name": "무너지는 환영", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 110, "def_down": 0.15, "duration": 3},
    "hunt_march7th": {"name": "결정적 순간의 포착", "dmg_mult": 1.44, "target": "single_enemy", "energy_cost": 110},
    "rappa": {"name": "봉인해방", "target": "single_ally", "energy_cost": 140, "atk_buff": 0.20, "duration": 2},
    "evernight": {"name": "가장 어두운 수수께끼", "dmg_mult": 2.0, "target": "all_enemies", "energy_cost": 240, "summon": True},
    "sunday": {"name": "지복의 인도", "target": "single_ally", "energy_cost": 130, "atk_buff": 0.25, "duration": 3},
    "ruanmei": {"name": "만물의 재구성", "dmg_mult": 0.3, "target": "all_enemies", "energy_cost": 130, "def_down": 0.2, "duration": 2},
    "clara": {"name": "스바로그의 응답", "target": "single_ally", "energy_cost": 110, "atk_buff": 0.20, "duration": 2},
    "jiaoqiu": {"name": "재로 돌아간 흔적", "dmg_mult": 0.6, "target": "all_enemies", "energy_cost": 100, "def_down": 0.15, "duration": 3},
    "cyrene": {"name": "회고의 물결", "target": "single_ally", "energy_cost": 240, "atk_buff": 0.30, "duration": 3},
    "aventurine": {"name": "판돈은 크게", "dmg_mult": 1.6, "target": "single_enemy", "energy_cost": 110},
    "cerydra": {"name": "군공을 세우다", "dmg_mult": 1.44, "target": "all_enemies", "energy_cost": 130},
    "sushang": {"name": "일도양단", "dmg_mult": 1.92, "target": "single_enemy", "energy_cost": 120},
    "acheron": {"name": "레인블레이드·환멸", "dmg_mult": 2.3, "target": "single_enemy", "energy_cost": 90},
    "lynx": {"name": "정화의 손길", "target": "all_allies", "energy_cost": 100, "heal_ratio": 0.12},
    "fugue": {"name": "겁화의 인장", "dmg_mult": 1.0, "target": "all_enemies", "energy_cost": 130},
    "anaxa": {"name": "승화", "dmg_mult": 0.8, "target": "all_enemies", "energy_cost": 140},
    "drratio": {"name": "현자의 우행", "dmg_mult": 1.44, "target": "single_enemy", "energy_cost": 140},
    "welt": {"name": "블랙홀의 감옥", "dmg_mult": 0.9, "target": "all_enemies", "energy_cost": 120, "spd_down": 0.1, "duration": 1},
    "huohuo": {"name": "생명 재충전", "target": "all_allies", "energy_cost": 140, "atk_buff": 0.24, "duration": 2},
    "hanya": {"name": "찰나에 지나치다", "target": "single_ally", "energy_cost": 140, "atk_buff": 0.36, "spd_buff": 0.15, "duration": 2},
    "bronya": {"name": "지고한 심판자의 강림", "target": "all_allies", "energy_cost": 120, "atk_buff": 0.33, "duration": 2},
    "sparkle": {"name": "위장한 진실", "target": "all_allies", "energy_cost": 110, "atk_buff": 0.20, "duration": 2},
    "mydei": {"name": "신 죽이는 자가 되어라", "dmg_mult": 1.6, "target": "single_enemy", "energy_cost": 160},
    "theherta": {"name": "재정렬된 해석", "dmg_mult": 1.0, "target": "all_enemies", "energy_cost": 220},
    "topaznumby": {"name": "윈드폴 보너스", "dmg_mult": 1.75, "target": "single_enemy", "energy_cost": 130},
    "kafka": {"name": "이올 044를 향한 왈츠", "dmg_mult": 0.48, "target": "all_enemies", "energy_cost": 120, "dot_ratio": 1.16, "duration": 2},
    "archer": {"name": "무한의 검제", "dmg_mult": 6.0, "target": "single_enemy", "energy_cost": 220},
    "silverwolf": {"name": "시스템 강제 종료", "dmg_mult": 2.28, "target": "single_enemy", "energy_cost": 110, "def_down": 0.36, "duration": 3},
    "silverwolf999": {"name": "갓 모드: ON!", "dmg_mult": 2.0, "target": "all_enemies", "energy_cost": 110},
    "jade": {"name": "저당잡힌 미래", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 140},
    "robin": {"name": "콘서트의 시작", "target": "all_allies", "energy_cost": 160, "atk_buff": 0.20, "duration": 2},
    "dahlia": {"name": "만개 직전의 시듦", "dmg_mult": 1.8, "target": "all_enemies", "energy_cost": 130, "def_down": 0.15, "duration": 4},
    "preservation_tb": {"name": "작열하는 방벽", "dmg_mult": 0.7, "target": "all_enemies", "energy_cost": 120},
    "guinaifen": {"name": "타오르는 소문", "dmg_mult": 0.72, "target": "all_enemies", "energy_cost": 120},
    "hyacine": {"name": "비 갠 뒤", "target": "all_allies", "energy_cost": 140, "heal_ratio": 0.11},
    "fuxuan": {"name": "운명의 저울", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 135},
    "cipher": {"name": "이중 위장", "dmg_mult": 0.6, "target": "single_enemy", "energy_cost": 130},
    "pela": {"name": "무장해제", "dmg_mult": 0.6, "target": "all_enemies", "energy_cost": 110, "def_down": 0.3, "duration": 2},
    "misha": {"name": "무한 연격", "dmg_mult": 1.0, "target": "single_enemy", "energy_cost": 100},

    # --- 최신/콜라보 캐릭터 (2026년 검색으로 확인) ---
    "ashveil": {"name": "미끼를 문 자", "dmg_mult": 3.0, "target": "single_enemy", "energy_cost": 140, "def_down": 0.2, "duration": 2},
    "evanescia": {"name": "검가: 사면 없는 참수", "dmg_mult": 2.4, "target": "all_enemies", "energy_cost": 240},
    "sparxie": {"name": "무대는 나의 것", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 130},
    "yaoguang": {"name": "깃털 든 운명의 육망성", "target": "all_allies", "energy_cost": 130, "atk_buff": 0.20, "duration": 2},
    "mortenax_blade": {"name": "무한한 분노", "dmg_mult": 1.0, "target": "single_enemy", "energy_cost": 160, "def_down": 0.2, "duration": 3},
    "himeko_nova": {"name": "궤도 섬멸 파동", "dmg_mult": 3.0, "target": "all_enemies", "energy_cost": 130},
    "gilgamesh": {"name": "왕의 재보", "dmg_mult": 2.5, "target": "all_enemies", "energy_cost": 200},
    "tohsaka_rin": {"name": "보석궁 마술", "dmg_mult": 1.6, "target": "all_enemies", "energy_cost": 120},
    "tribbie": {"name": "재판정 영역", "dmg_mult": 1.5, "target": "all_enemies", "energy_cost": 120},
    "remembrance_tb": {"name": "메모스프라이트 소환: 멤", "dmg_mult": 1.2, "target": "all_enemies", "energy_cost": 160, "summon": True},
    "elation_tb": {  # 지정 아군 치명타 피해 강화 + 제어류 디버프 해제(치명타 피해 버프로 근사)
        "name": "웃음 포인트 증정", "target": "single_ally", "energy_cost": 140,
        "atk_buff": 0.30, "duration": 3,
    },
}


def _apply_real_ultimates():
    for key, ult in REAL_ULTIMATES.items():
        if key in SKILLS:
            SKILLS[key]["ultimate"] = ult


_apply_real_ultimates()
