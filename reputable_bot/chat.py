import asyncio
from asyncio import Task
from asyncio import create_task
from asyncio import sleep
import logging
import json
from pathlib import Path
from typing import cast

from . import env
from . import ollama

#import markovify
from discord import Message
from discord import TextChannel

log = logging.getLogger(__name__)

# context
context: list[int] = []
context_saving_task: Task

# Channel config
ignored_channels: list[TextChannel] = []

async def generate_message(prompt: str, update_global_context: bool = False) -> str:
    global context
    message = await ollama.generate_from_prompt(
        prompt=prompt,
        context=context,
        url=env.REPBOT_OLLAMA_URL,
        model=env.REPBOT_DEFAULT_MODEL,
        system=env.REPBOT_SYSTEM_MESSAGE,
    )
    if update_global_context:
        context = message[1]
    return message[0]


async def save_context_routine(context_path: Path):
    while True:
        log.info(f"Saving context to {context_path}.")
        with open(context_path, "w") as f:
            f.write(json.dumps(context))
        log.info("Context saved!")
        await sleep(60)

async def respond(message: Message):
    try:
        channel: TextChannel = cast(TextChannel, message.channel)
        
        log.info("Generating a response...")
        for i in range(4):
            prompt: str = (f"{message.author.display_name}: {message.content}\nreputablebot: ")
            response = await generate_message(prompt, True)
            if len(response) > 2000:
                log.warn(f"Generated too long of a response, retrying [{i+1}/4]")
                continue
            log.info(f"Sending response: {response}")
            await channel.send(response)
            return
        log.error("Failed to generate a suitable response!")

        await channel.send("fug i messed that one up and couldnt generate a suitable message, that sucks hey")
    except TypeError as error:
        log.error(f"{message.channel} is not a valid text channel: {error}")


async def init(context_path: Path) -> bool:
    # load context
    global context
    global context_saving_task
    log.info(f"Loading LLM context from {context_path}...")
    try:
        with open(context_path, "r") as f:
            context = json.loads(f.read())
    except FileNotFoundError:
        log.warn(f"No LLM context saved at {context_path}! Proceeding with empty context.")
    except json.JSONDecodeError:
        log.warn(f"{context_path} does not contain valid JSON! Proceeding with empty context.")
    log.info(
        "Initialising chat:"
        + f"\n\tContext size: {len(context)}"
        + f"\n\tChat LLM: {env.REPBOT_DEFAULT_MODEL}"
        + f"\n\tContext path: {context_path}"
    )
    log.info("Starting context saving task...")
    context_saving_task = create_task(save_context_routine(context_path))

