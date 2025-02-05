import asyncio

import loader
from data import config

from handlers.user.start import user_router

from loguru import logger


async def on_startup():
    loader.dp.include_router(user_router)
    await loader.dp.start_polling(loader.bot)
    logger.info("Bot started in longpoll mode")

if __name__ == '__main__':
    asyncio.run(on_startup())
