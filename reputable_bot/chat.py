import logging
import json
from pathlib import Path

from . import env

import markovify

log = logging.getLogger("reputable_chat")


context: list[int] = []

async def generate_message(prompt: str, update_global_context: bool = False) -> str:
    global context


# async def save_context(context_path: Path):

async def init(context_path: Path) -> bool:
    # load context
    log.info(f"Loading LLM context from {context_path}...")
    try:
        with open(context_path, "r") as f:
            json.loads(f.read())
    except FileNotFoundError:
        log.warn(f"No LLM context saved at {context_path}! Proceeding with empty context.")
    except json.JSONDecodeError:
        log.warn(f"{context_path} does not contain valid JSON! Proceeding with empty context.")
    log.info(
        "Initialising chat:"
        + f"\n\tContext size: {len(context)}"
        + f"\n\tChat LLM: {env.REPBOT_DEFAULT_MODEL}"
    )
