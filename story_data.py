"""
분기형 스토리 데이터.

각 노드는 다음 구조를 가집니다:
{
    "text": "화면에 보여줄 이야기",
    "image": None 또는 이미지 URL,
    "choices": [
        {
            "label": "버튼에 표시될 텍스트",
            "next": "다음 노드 id",
            "requires_flag": None 또는 (flag_name, value),  # 이 조건을 만족해야 선택지가 보임
            "set_flag": None 또는 (flag_name, value),       # 선택 시 세팅되는 플래그
        },
        ...
    ],
    "ending": False 또는 "엔딩 이름" (엔딩 노드일 경우)
}

원작 게임의 대사나 설정을 그대로 베끼지 않고, 우주선/은하철도 컨셉만 참고한
오리지널 캐릭터·세계관으로 구성했습니다. 캐릭터 이름이나 지명은 자유롭게
바꿔서 쓰세요.
"""

STORY = {
    "start": {
        "text": (
            "은하철도 '노바 익스프레스'가 정체불명의 신호를 받고 궤도를 이탈했다.\n"
            "눈을 뜨니 당신은 화물칸 바닥에 쓰러져 있고, 창밖에는 본 적 없는 붉은 성운이 펼쳐져 있다.\n"
            "복도 저편에서 발소리가 들려온다."
        ),
        "image": None,
        "choices": [
            {"label": "발소리 쪽으로 향한다", "next": "meet_ally", "requires_flag": None, "set_flag": None},
            {"label": "조용히 화물칸에 숨는다", "next": "hide_cargo", "requires_flag": None, "set_flag": ("cautious", True)},
        ],
        "ending": False,
    },
    "meet_ally": {
        "text": (
            "복도 끝에서 정비복을 입은 항해사 '리안'과 마주친다.\n"
            "\"살아있었네. 엔진실이 반쯤 날아갔어. 도와줄 거야, 아니면 구경만 할 거야?\""
        ),
        "image": None,
        "choices": [
            {"label": "\"당연히 돕겠다\"고 말한다", "next": "engine_room", "requires_flag": None, "set_flag": ("trust_rian", True)},
            {"label": "일단 상황부터 설명해달라고 한다", "next": "explanation", "requires_flag": None, "set_flag": None},
        ],
        "ending": False,
    },
    "hide_cargo": {
        "text": (
            "당신은 상자 뒤에 몸을 숨긴다.\n"
            "발소리의 주인공, 항해사 '리안'이 화물칸을 지나치며 혼잣말을 한다.\n"
            "\"...아무도 없나. 엔진실부터 확인해야겠어.\"\n"
            "그녀가 떠난 뒤, 당신은 혼자 남았다."
        ),
        "image": None,
        "choices": [
            {"label": "몰래 뒤따라간다", "next": "engine_room", "requires_flag": None, "set_flag": None},
            {"label": "반대 방향, 조종실로 향한다", "next": "cockpit_alone", "requires_flag": None, "set_flag": None},
        ],
        "ending": False,
    },
    "explanation": {
        "text": (
            "\"신호를 쫓다가 항로를 이탈했어. 지금 엔진 출력이 널뛰고 있고,\n"
            "이대로면 성운 안으로 빨려 들어가. 시간이 없어.\"\n"
            "리안이 다급하게 덧붙인다. \"결정해. 엔진실이야, 조종실이야?\""
        ),
        "image": None,
        "choices": [
            {"label": "엔진실로 간다", "next": "engine_room", "requires_flag": None, "set_flag": None},
            {"label": "조종실로 간다", "next": "cockpit_together", "requires_flag": None, "set_flag": None},
        ],
        "ending": False,
    },
    "engine_room": {
        "text": (
            "엔진실은 불꽃과 연기로 가득하다.\n"
            "핵심 냉각 장치가 과부하 직전이다. 수동으로 냉각재를 주입할 시간은 단 몇 초뿐."
        ),
        "image": None,
        "choices": [
            {
                "label": "냉각재를 즉시 수동 주입한다 (위험)",
                "next": "ending_hero",
                "requires_flag": None,
                "set_flag": None,
            },
            {
                "label": "리안과 함께 안전 절차대로 진행한다",
                "next": "ending_team",
                "requires_flag": ("trust_rian", True),
                "set_flag": None,
            },
        ],
        "ending": False,
    },
    "cockpit_alone": {
        "text": (
            "혼자 도착한 조종실. 계기판이 붉게 점멸한다.\n"
            "당신 힘만으로 항로를 되돌릴 수 있을까?"
        ),
        "image": None,
        "choices": [
            {"label": "수동 조타를 시도한다", "next": "ending_lone_pilot", "requires_flag": None, "set_flag": None},
        ],
        "ending": False,
    },
    "cockpit_together": {
        "text": (
            "리안과 함께 조종실에 도착한다.\n"
            "\"내가 출력을 잡을 테니, 네가 항로를 잡아!\" 그녀가 외친다."
        ),
        "image": None,
        "choices": [
            {"label": "항로를 성운 바깥으로 튼다", "next": "ending_team", "requires_flag": None, "set_flag": None},
        ],
        "ending": False,
    },
    "ending_hero": {
        "text": (
            "당신은 홀로 냉각재를 주입해 폭발을 막아낸다.\n"
            "화상을 입었지만, 노바 익스프레스는 살아남았다.\n"
            "리안이 뒤늦게 도착해 당신을 발견하고 놀란다.\n\n"
            "🌟 엔딩: '고독한 영웅'"
        ),
        "image": None,
        "choices": [],
        "ending": "고독한 영웅",
    },
    "ending_team": {
        "text": (
            "당신과 리안은 함께 위기를 넘긴다.\n"
            "성운을 벗어난 노바 익스프레스 함교에서, 리안이 처음으로 미소를 보인다.\n"
            "\"다음에도 이렇게 같이 가자.\"\n\n"
            "🌟 엔딩: '동료'"
        ),
        "image": None,
        "choices": [],
        "ending": "동료",
    },
    "ending_lone_pilot": {
        "text": (
            "당신 혼자 조타간을 붙잡고 사투를 벌인 끝에,\n"
            "가까스로 성운을 빠져나온다. 하지만 리안은 끝내 만나지 못했다.\n\n"
            "🌟 엔딩: '홀로 선 항해사'"
        ),
        "image": None,
        "choices": [],
        "ending": "홀로 선 항해사",
    },
}

START_NODE = "start"
