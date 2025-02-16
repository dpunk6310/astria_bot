import asyncio
import logging
import sys

from loguru import logger as log

import loader
from handlers.avatar import setup as avatar_setup
from handlers.gen_photo import setup as gen_photo_setup
from handlers.god_mod import setup as god_mod_setup
from handlers.info import setup as info_setup
from handlers.payment import setup as payment_setup
from handlers.support import setup as support_setup
from handlers.gen_video import setup as gen_video_setup


async def on_startup():
    info_setup(loader.dp)
    gen_photo_setup(loader.dp)
    avatar_setup(loader.dp)
    payment_setup(loader.dp)
    support_setup(loader.dp)
    gen_video_setup(loader.dp)
    god_mod_setup(loader.dp)
    
    await loader.dp.start_polling(loader.bot)
    

if __name__ == '__main__':
    log.info("Bot started in longpoll mode")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(on_startup())
