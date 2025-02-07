import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))


BOT_TOKEN = env.str("BOT_TOKEN", default="norm")
PLACE = env.str("PLACE", default="test")
DJANGO_URL = env.str("DJANGO_URL")
REDIS_PASSWORD = env.str("REDIS_PASSWORD", "")
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", "6379")
REDIS_DB = env.str("REDIS_DB", "0")

ROBOKASSA_MERCHANT_ID = env.str("ROBOKASSA_MERCHANT_ID", "")
ROBOKASSA_PASSWORD1 = env.str("ROBOKASSA_PASSWORD1", "")
ROBOKASSA_PASSWORD2 = env.str("ROBOKASSA_PASSWORD2", "")
ROBOKASSA_TEST_PASSWORD1 = env.str("ROBOKASSA_TEST_PASSWORD1", "")
ROBOKASSA_TEST_PASSWORD2 = env.str("ROBOKASSA_TEST_PASSWORD2", "")

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
