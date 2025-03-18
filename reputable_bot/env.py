import logging
import os

log = logging.getLogger("repbot")

REPBOT_DISCORD_API_TOKEN: str | None = None
REPBOT_DEFAULT_CHANNEL_ID: str | int | None = None
REPBOT_DUNGEON_CHANNEL_ID: str | int | None = None
REPBOT_LOG_LEVEL: str | int | None = None
REPBOT_OLLAMA_URL: str | None = None
REPBOT_DEFAULT_MODEL: str | None = None
REPBOT_SYSTEM_MESSAGE: str | None = None
REPBOT_CONTEXT_WINDOW: str | None = None


def setup():
    global REPBOT_DISCORD_API_TOKEN
    global REPBOT_DEFAULT_CHANNEL_ID
    global REPBOT_DUNGEON_CHANNEL_ID
    global REPBOT_LOG_LEVEL
    global REPBOT_OLLAMA_URL
    global REPBOT_DEFAULT_MODEL
    global REPBOT_SYSTEM_MESSAGE
    global REPBOT_CONTEXT_WINDOW

    REPBOT_DISCORD_API_TOKEN = os.getenv("REPBOT_DISCORD_API_TOKEN")
    REPBOT_DEFAULT_CHANNEL_ID = os.getenv("REPBOT_DEFAULT_CHANNEL_ID")
    REPBOT_DUNGEON_CHANNEL_ID = os.getenv("REPBOT_DUNGEON_CHANNEL_ID")
    REPBOT_LOG_LEVEL = os.getenv("REPBOT_LOG_LEVEL")
    REPBOT_OLLAMA_URL = os.getenv("REPBOT_OLLAMA_URL")
    REPBOT_DEFAULT_MODEL = os.getenv("REPBOT_DEFAULT_MODEL")
    REPBOT_SYSTEM_MESSAGE = os.getenv("REPBOT_SYSTEM_MESSAGE")
    REPBOT_CONTEXT_WINDOW = os.getenv("REPBOT_CONTEXT_WINDOW")

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

    if REPBOT_CONTEXT_WINDOW:
        try:
            REPBOT_CONTEXT_WINDOW = int(REPBOT_CONTEXT_WINDOW)
        except ValueError:
            log.warning(
                "REPBOT_CONTEXT_WINDOW was not set to a valid integer. Defaulting to 2048 tokens."
            )
            REPBOT_CONTEXT_WINDOW = None
    if not REPBOT_CONTEXT_WINDOW:
        REPBOT_CONTEXT_WINDOW = 2048

    if not REPBOT_DISCORD_API_TOKEN:
        log.error(
            "REPBOT_DISCORD_API_TOKEN is not set. A valid Discord API token is required to authenticate."
        )
        exit(1)

    if not REPBOT_OLLAMA_URL:
        log.warning(
            "REPBOT_OLLAMA_URL is not set. Defaulting to 'http://localhost:11343'"
        )
        REPBOT_OLLAMA_URL = "http://localhost:11343"

    if not REPBOT_DEFAULT_MODEL:
        log.warning("REPBOT_DEFAULT_MODEL is not set. Defaulting to 'llama3.1:8b'")
        REPBOT_DEFAULT_MODEL = "llama3.1:8b"

    if REPBOT_SYSTEM_MESSAGE is None:
        log.warning("REPBOT_SYSTEM_MESSAGE is not set. Using default system message.")
        REPBOT_SYSTEM_MESSAGE = open("system.txt", "r").read()

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

    if not REPBOT_DUNGEON_CHANNEL_ID:
        log.warning("REPBOT_DUNGEON_CHANNEL_ID is not set. This feature is disabled.")
        REPBOT_DUNGEON_CHANNEL_ID = None
    else:
        try:
            REPBOT_DUNGEON_CHANNEL_ID = int(REPBOT_DUNGEON_CHANNEL_ID)
        except ValueError:
            log.warning(
                "REPBOT_DUNGEON_CHANNEL_ID is not set to a valid integer. This feature is disabled."
            )
            REPBOT_DUNGEON_CHANNEL_ID = None
