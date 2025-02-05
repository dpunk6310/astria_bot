import asyncio
from pathlib import Path

import loader
from data import config

from handlers.user.start import user_router

from loguru import logger as log


async def on_startup():
    loader.dp.include_router(user_router)
    await loader.dp.start_polling(loader.bot)
    

if __name__ == '__main__':
    log.info("Bot started in longpoll mode")
    asyncio.run(on_startup())
