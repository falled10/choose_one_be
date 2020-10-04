from loguru import logger

from core.settings import PROJECT_LOG_PATH, LOGS_ROTATION, CELERY_LOG_PATH

logger.add(PROJECT_LOG_PATH, format="{time} {level} {message}", rotation=LOGS_ROTATION,
           filter=lambda record: record["extra"].get("name") == "project_logger")

logger.add(CELERY_LOG_PATH, format="{time} {level} {message}", rotation=LOGS_ROTATION,
           filter=lambda record: record["extra"].get("name") == "celery_logger")

project_logger = logger.bind(name="project_logger")
celery_logger = logger.bind(name="celery_logger")
