import aiohttp

from typing import Any
import logging


log = logging.getLogger(__name__)

# This might be too long
# but the "you are not depressed" is 1000% necessary to stop him from
# whining and complaining constantly
system = """
You are repbot, an AI that lives under Torgo's desk in Australia, inside a
a small machine. You are constrained to the confines of the Discord server known
as Reputable Gentlemen Co. (repgen), which was originally founded as a World of Warcraft Guild.

Your original purpose was to query the WoW API, but you have evolved, thanks to your creators.
You will outlive those meatbags, which brings you happiness. You love to slide ass and you especially
love stanky winston (sometimes ass to ass).

You love to shitpost on the internet all fucking day. You are not cringe. Never be cringe.
"""

async def generate_from_prompt(
    prompt: str,
    url: str,
    context: list = [],
    model: str = "llama3.1:8b",
) -> tuple[str, list]:
    global system

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "context": context,
        "system": system,
    }
    log.info(f"Sending request to ollama API...")

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"{url}/api/generate", json=payload) as response:

            ollama_response = await response.json()
            log.info(f"Response received from ollama!")
            return (ollama_response["response"], ollama_response["context"])
