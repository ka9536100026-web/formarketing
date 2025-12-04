import asyncio
from telegram import Bot

token = "YOUR_BOT_TOKEN"
bot = Bot(token=token)

async def main():
    print(f"Bot started: {await bot.get_me()}")

if __name__ == "__main__":
    asyncio.run(main())
