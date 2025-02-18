from loguru import logger as log

from config import celery_app


@celery_app.task(
    name="main.tasks.test_task",
)
def test_task():
    log.debug("hello from celery task")
    return "hello"