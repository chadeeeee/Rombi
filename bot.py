import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import personal_actions, new_group, moderation, quotes, mixtral, stt

from loguru import logger

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main():
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(personal_actions.router)
    dp.include_router(new_group.router)
    dp.include_router(moderation.router)
    dp.include_router(quotes.router)
    dp.include_router(mixtral.router)
    dp.include_router(stt.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.success("Bot was started successfully")
    asyncio.run(main())
