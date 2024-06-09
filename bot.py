import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import personal_actions, new_group

from loguru import logger


async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(personal_actions.router)
    dp.include_router(new_group.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.success("Bot was started successfully")
    asyncio.run(main())
