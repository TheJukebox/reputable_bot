import json
import os
import datetime
from typing import AsyncGenerator
from pathlib import Path

from . import env
from . import logging

import discord

log = logging.setup_log(__name__)
log.setLevel(env.REPBOT_LOG_LEVEL)


async def fetch_messages(channel: discord.TextChannel, n: int) -> AsyncGenerator:
    async for message in channel.history(limit=n):
        yield {
            "message_id": message.id,
            "author_id": message.author.id,
            "author_display_name": message.author.display_name,
            "content": message.clean_content,
            "created_at": message.created_at.isoformat(),
            "channel": message.channel.id,
            "pinned": message.pinned,
        }


async def write_message_data(channel: discord.TextChannel, size: int) -> str:
    log.info(f"Fetching images for channel {channel.name} ({channel.id})...")
    messages = fetch_messages(channel, size)
    data = []
    path: Path = Path(
        f"repbot-{size}_messages-{datetime.datetime.now().timestamp()}.json"
    )
    with open(path, "w") as f:
        async for message in messages:
            data.append(message)
        f.write(json.dumps(data))
    return str(path.absolute())
