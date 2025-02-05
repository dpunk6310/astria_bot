import asyncio

from bot import loader
from bot.initial_data import initialize_data
from bot.data import config

from bot.handlers import setup

from loguru import logger

async def on_startup():
    setup(loader.dp)
    initialize_data()
    await loader.dp.start_polling()
    logger.info("Bot started in longpoll mode")

if __name__ == '__main__':
    asyncio.run(on_startup())
