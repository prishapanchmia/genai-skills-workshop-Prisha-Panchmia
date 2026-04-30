import logging
from google.cloud import logging as cloud_logging

cloud_logging.Client().setup_logging()

logger = logging.getLogger("ads-agent")
logger.setLevel(logging.INFO)
