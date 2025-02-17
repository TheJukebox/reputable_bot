import aiohttp

from . import env

from typing import Any
import logging


log = logging.getLogger(__name__)

# This might be too long
# but the "you are not depressed" is 1000% necessary to stop him from
# whining and complaining constantly


async def generate_from_prompt(
    prompt: str,
    url: str,
    context: list = [],
    model: str = "llama3.1:8b",
) -> tuple[str, list]:

    system = env.REPBOT_SYSTEM_MESSAGE

    log.info("Generating completion with:")
    log.info(f"System: {system}")
    log.info(f"Prompt: {prompt}")
    log.info(f"Context window of {env.REPBOT_CONTEXT_WINDOW} tokens.")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "context": context,
        "system": system,
        "option": {
            "num_ctx": env.REPBOT_CONTEXT_WINDOW,
            "temperature": 0.9,
            "repeat_last_n": -1,
            "repeat_penalty": 1.1,
        },
    }
    log.info(f"Sending request to ollama API...")

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"{url}/api/generate", json=payload) as response:

            ollama_response = await response.json()
            log.info(f"Response received from ollama!")
            return (ollama_response["response"], ollama_response["context"])
