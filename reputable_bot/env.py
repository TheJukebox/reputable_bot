import logging
import os

log = logging.getLogger(__name__)

REPBOT_DISCORD_API_TOKEN: str | None = None
REPBOT_DEFAULT_CHANNEL_ID: str | int | None = None
REPBOT_LOG_LEVEL: str | int | None = None
REPBOT_OLLAMA_URL: str | None = None 
REPBOT_DEFAULT_MODEL: str | None = None


def setup():
    global REPBOT_DISCORD_API_TOKEN
    global REPBOT_DEFAULT_CHANNEL_ID
    global REPBOT_LOG_LEVEL
    global REPBOT_OLLAMA_URL
    global REPBOT_DEFAULT_MODEL

    REPBOT_DISCORD_API_TOKEN = os.getenv("REPBOT_DISCORD_API_TOKEN")
    REPBOT_DEFAULT_CHANNEL_ID = os.getenv("REPBOT_DEFAULT_CHANNEL_ID")
    REPBOT_LOG_LEVEL = os.getenv("REPBOT_LOG_LEVEL")
    REPBOT_OLLAMA_URL = os.getenv("REPBOT_OLLAMA_URL")
    REPBOT_DEFAULT_MODEL = os.getenv("REPBOT_DEFAULT_MODEL")

    if not REPBOT_LOG_LEVEL:
        log.info("REPBOT_LOG_LEVEL not set. Defaulting to 'info'")
        REPBOT_LOG_LEVEL = logging.INFO
    elif REPBOT_LOG_LEVEL == "debug":
        log.info("REPBOT_LOG_LEVEL set to 'debug'")
        REPBOT_LOG_LEVEL = logging.DEBUG
    elif REPBOT_LOG_LEVEL == "error":
        log.info("REPBOT_LOG_LEVEL set to 'error'")
        REPBOT_LOG_LEVEL = logging.ERROR
    else:
        log.info("REPBOT_LOG_LEVEL set to 'info'")
        REPBOT_LOG_LEVEL = logging.INFO

    if not REPBOT_OLLAMA_URL:
        log.warn("REPBOT_OLLAMA_RUL is not set. Defaulting to 'http://localhost:11343'")
        REPBOT_OLLAMA_URL = "http://localhost:11343"

    if not REPBOT_DEFAULT_MODEL:
        log.warn("REPBOT_DEFAULT_MODEL is not set. Defaulting to 'llama3.1:8b'")
        REPBOT_DEFAULT_MODEL = "llama3.1:8b"

    if not REPBOT_DISCORD_API_TOKEN:
        log.error(
            "REPBOT_DISCORD_API_TOKEN is not set. A valid Discord API token is required to authenticate."
        )
        exit(1)

    if not REPBOT_DEFAULT_CHANNEL_ID:
        log.warning(
            "REPBOT_DEFAULT_CHANNEL_ID is not set. The bot will join a channel randomly to announce itself."
        )
        REPBOT_DEFAULT_CHANNEL_ID = None
    else:
        try:
            REPBOT_DEFAULT_CHANNEL_ID = int(REPBOT_DEFAULT_CHANNEL_ID)
        except ValueError:
            log.warning(
                "REPBOT_DEFAULT_CHANNEL_ID is not set to a valid integer. The bot will join a channel randomly to announce itself."
            )
            REPBOT_DEFAULT_CHANNEL_ID = None
