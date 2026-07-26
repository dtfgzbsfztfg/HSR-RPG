# 은하철도 스토리 디스코드 봇 (RPG 선택지 게임)

붕괴: 스타레일 느낌의 "은하철도" 세계관에서, 선택에 따라 이야기가 갈라지는
디스코드 봇입니다. 원작 대사/설정을 그대로 복사하지 않고 오리지널 스토리로
구성했으니, 캐릭터 이름이나 세계관은 `story_data.py`에서 자유롭게 바꿔 쓰세요.

## 폴더 구조

```
starrail_bot/
├── bot.py              # 실행 진입점
├── database.py         # 유저 진행상황 저장 (SQLite)
├── story_data.py        # 분기 스토리 데이터 (여기를 수정해서 이야기 확장)
├── cogs/
│   └── story.py         # /start, /status, /reset 명령어 + 버튼 UI
└── requirements.txt
```

## 실행 방법

1. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **디스코드 봇 생성**
   - https://discord.com/developers/applications 에서 New Application
   - Bot 탭에서 Reset Token → 토큰 복사
   - Bot 탭에서 **Message Content Intent** 켜기 (텍스트 `!1` 입력 처리용)
   - OAuth2 → URL Generator에서 scope: `bot`, `applications.commands` 체크,
     권한은 `Send Messages`, `Embed Links`, `Read Message History` 정도면 충분
   - 생성된 URL로 봇을 본인 서버에 초대

3. **토큰 환경변수 설정 후 실행**
   ```bash
   export DISCORD_BOT_TOKEN=여기에_토큰_붙여넣기
   python bot.py
   ```

4. 디스코드 채널에서 `/start` 입력 → 스토리 시작!
   - 버튼을 눌러도 되고, `!1`, `!2` 처럼 채팅으로 입력해도 선택됩니다.
   - `/status`로 현재 진행 상황(플래그) 확인
   - `/reset`으로 처음부터 다시 시작

## 스토리 확장하는 법

`story_data.py`의 `STORY` 딕셔너리에 노드를 추가하면 됩니다.

```python
"새로운_노드_id": {
    "text": "여기에 이야기 내용",
    "image": None,  # 이미지 URL을 넣으면 임베드에 표시됨
    "choices": [
        {
            "label": "선택지 문구",
            "next": "다음_노드_id",
            "requires_flag": None,          # 예: ("trust_rian", True) 처럼 조건부 선택지도 가능
            "set_flag": None,               # 예: ("met_rian", True) 선택 시 플래그 저장
        },
    ],
    "ending": False,  # 엔딩 노드면 "엔딩 이름" 문자열
},
```

- `requires_flag`를 걸면 특정 조건(이전 선택)을 만족했을 때만 그 선택지가 나타납니다.
  → 이걸로 "히든 루트", "캐릭터 호감도 분기" 같은 걸 만들 수 있어요.
- `stats`(체력, 능력치 등)를 활용하고 싶으면 `database.py`의 `stats` 필드에
  숫자를 저장하고, story 진행 로직에서 조건 분기를 추가하면 됩니다.

## 전투 (글룸헤이븐 스타일)

`/fight 몬스터종류 [인원수]` 로 전투를 시작합니다. (예: `/fight 우주해적 2`)

1. **파티 구성**: 채널에 뜬 메시지에서 "돌격병으로 참가" / "저격수로 참가" 버튼을 눌러 합류
   (여러 명이 같은 전투에 참가 가능 = 파티 플레이, 혼자 참가해도 됨 = 솔로 플레이)
2. 준비되면 아무나 **"전투 시작"** 클릭
3. 매 라운드, 각자 **"카드 선택"** 버튼 → 드롭다운에서 카드 1장 선택
   - 카드에는 이니셔티브(행동 순서, 낮을수록 먼저), 이동/공격 정보가 표시됨
4. 전원이 카드를 고르면 자동으로:
   - 이니셔티브 순으로 정렬 후 각자 행동 실행
   - 이동은 가장 가까운 적 쪽으로 자동 이동 (5x5 그리드, 사거리/근접 판정에 사용)
   - 공격은 사거리 안의 가장 가까운 적을 자동 타겟, 수정자 카드(+0~+2, -1~-2, x2, MISS)를 뽑아 데미지 결정
5. 몬스터 전멸 시 승리, 파티 전멸 시 패배. 손패를 다 쓰면 자동으로 "짧은 휴식"(카드 회수 + HP 소량 회복)

`/fight_classes` 로 직업 목록/설명을 볼 수 있어요.

전투 관련 파일:
- `combat/combat_data.py` — 직업 카드 덱, 몬스터 스탯/AI 덱, 수정자 덱 (여기서 밸런스 조정·직업 추가)
- `combat/engine.py` — 그리드, 이동/공격 판정, 라운드 진행 로직
- `cogs/combat.py` — `/fight` 명령어, 파티 참가·카드 선택 버튼 UI

새 직업을 추가하려면 `combat_data.py`의 `CLASSES`에 항목을 추가하고, 새 몬스터는
`MONSTER_TYPES`에 추가하면 됩니다.

## 다음에 추가하면 좋은 것들

- 전투 시스템 (스탯 기반 간단한 주사위 판정)
- 인벤토리/아이템 시스템 (이미 `inventory` 필드는 준비되어 있음)
- 여러 챕터 파일로 분리 (`story_data_ch1.py`, `story_data_ch2.py` 등)
- 이미지/캐릭터 일러스트 임베드에 첨부 (자체 제작 이미지 사용 권장 — 저작권 이슈 방지)

## 주의사항 (저작권)

비상업적 팬 프로젝트이지만, 원작 게임의 대사·삽화·로고를 그대로 가져다 쓰는 건
피하는 게 안전해요. 세계관 분위기나 컨셉 정도만 참고하고, 텍스트/이미지는
직접 창작하시는 걸 추천합니다.
