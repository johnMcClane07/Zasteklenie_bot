import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import config
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, calculator,request,manager,faq,admin,examples,ai
from crm import init_crm

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
storage=MemoryStorage()

dp.include_router(start.router)
dp.include_router(calculator.router)
dp.include_router(request.router)
dp.include_router(manager.router)
dp.include_router(faq.router)
dp.include_router(admin.router)
dp.include_router(ai.router)
dp.include_router(examples.router)


async def main():
    init_crm()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())