import logging
import json
from asyncio import Task
from asyncio import sleep
from asyncio import create_task
from pathlib import Path

from . import env
from . import utils
from . import chat
from . import logging

from discord import TextChannel
from discord import Forbidden

log = logging.setup_log(__name__)
log.setLevel(env.REPBOT_LOG_LEVEL)

tasks: set[Task] = set()


async def cache_messages(channels: list[TextChannel]):
    while True:
        for channel in channels:
            log.info(f"Caching {channel}...")
            try:
                chat.message_cache[channel.id] = [
                    message["content"]
                    async for message in utils.fetch_messages(channel, 200)
                ]
                log.info(f"Cached {channel}!")
            except Forbidden:
                log.error(f"We were forbidden from accessing {channel}")
        await sleep(60)


async def cache_context(context_path: Path):
    while True:
        log.info(f"Saving context to {context_path}.")
        with open(context_path, "w") as f:
            f.write(json.dumps(chat.context))
        log.info("Context saved!")
        await sleep(60)
