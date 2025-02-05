from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from loguru import logger

# locale imports
from data.config import BOT_TOKEN
from data.config import PLACE

# bot
bot = Bot(token=BOT_TOKEN, validate_token=True)

if PLACE in ["locale", "test"]:
    storage = RedisStorage2()
elif PLACE == "host":
    storage = RedisStorage2(host="redisdb")
else:
    storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logger.add("logs/debug.log", diagnose=False)
