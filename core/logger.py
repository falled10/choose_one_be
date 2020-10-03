from loguru import logger

from core.settings import PROJECT_LOG_PATH, LOGS_ROTATION

logger.add(PROJECT_LOG_PATH, format="{time} {level} {message}", rotation=LOGS_ROTATION,
           filter=lambda record: record["extra"].get("name") == "project_logger")

project_logger = logger.bind(name="project_logger")
