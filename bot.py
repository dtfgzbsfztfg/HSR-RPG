"""
봇 실행 진입점.

실행 전 준비:
1. pip install -r requirements.txt
2. 환경변수 DISCORD_BOT_TOKEN 에 봇 토큰을 넣기
   (터미널에서: export DISCORD_BOT_TOKEN=여기에_토큰)
3. python bot.py

Discord 개발자 포털(https://discord.com/developers/applications)에서:
- 봇을 만들고 토큰 발급
- "Message Content Intent" 켜기 (텍스트 '!숫자' 입력 처리를 위해 필요)
- OAuth2 URL Generator에서 scope: bot, applications.commands 체크,
  권한: Send Messages, Embed Links, Read Message History 정도면 충분
"""
import os
import asyncio

import discord
from discord.ext import commands

import database

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print(f"로그인 완료: {bot.user} (id: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 커맨드 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"슬래시 커맨드 동기화 실패: {e}")


async def main():
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_BOT_TOKEN 환경변수가 설정되지 않았어요. "
            "봇 토큰을 환경변수로 넣어주세요."
        )
    await database.init_db()
    async with bot:
        await bot.load_extension("cogs.story")
        await bot.load_extension("cogs.combat")
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
