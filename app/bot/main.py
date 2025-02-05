import asyncio

from loguru import logger as log

import loader
from handlers.user.start import user_router


async def on_startup():
    loader.dp.include_router(user_router)
    await loader.dp.start_polling(loader.bot)
    
    

if __name__ == '__main__':
    log.info("Bot started in longpoll mode")
    asyncio.run(on_startup())
