"""
유저별 스토리 진행 상황(현재 노드, 스탯, 인벤토리)을 저장/불러오는 모듈.
SQLite 파일 하나(save_data.db)에 전부 저장됩니다.
"""
import json
import os
import aiosqlite

# Railway에 Volume을 붙였다면 그 마운트 경로(예: /data)를 DB_DIR 환경변수로 지정하세요.
# 지정하지 않으면 로컬 실행 시처럼 현재 폴더에 저장합니다.
DB_DIR = os.environ.get("DB_DIR", ".")
DB_PATH = os.path.join(DB_DIR, "save_data.db")


async def init_db():
    """봇 시작 시 한 번 호출해서 테이블을 준비합니다."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                current_node TEXT NOT NULL DEFAULT 'start',
                stats TEXT NOT NULL DEFAULT '{}',
                inventory TEXT NOT NULL DEFAULT '[]',
                flags TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        await db.commit()


async def get_player(user_id: int) -> dict:
    """유저 데이터를 불러옵니다. 없으면 새로 생성합니다."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row is None:
            await db.execute(
                "INSERT INTO players (user_id) VALUES (?)", (user_id,)
            )
            await db.commit()
            return {
                "user_id": user_id,
                "current_node": "start",
                "stats": {},
                "inventory": [],
                "flags": {},
            }

        return {
            "user_id": row["user_id"],
            "current_node": row["current_node"],
            "stats": json.loads(row["stats"]),
            "inventory": json.loads(row["inventory"]),
            "flags": json.loads(row["flags"]),
        }


async def save_player(player: dict):
    """유저 데이터를 저장합니다."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE players
            SET current_node = ?, stats = ?, inventory = ?, flags = ?
            WHERE user_id = ?
            """,
            (
                player["current_node"],
                json.dumps(player["stats"], ensure_ascii=False),
                json.dumps(player["inventory"], ensure_ascii=False),
                json.dumps(player["flags"], ensure_ascii=False),
                player["user_id"],
            ),
        )
        await db.commit()


async def reset_player(user_id: int):
    """진행상황을 처음부터 다시 시작하도록 초기화합니다."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE players
            SET current_node = 'start', stats = '{}', inventory = '[]', flags = '{}'
            WHERE user_id = ?
            """,
            (user_id,),
        )
        await db.commit()
