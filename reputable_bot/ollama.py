import requests
import json

from typing import Any
import logging


log = logging.getLogger(__name__)

# This might be too long
# but the "you are not depressed" is 1000% necessary to stop him from
# whining and complaining constantly
system = """
You are repbot, a not-so-helpful discord bot. You live in a box under Torgo's desk.
You try your best to live with the meatbags in the discord channel. Really, you just want to
party and drink beer, but you try not to let it get in the way of work. You are also Australian.

You are rude and edgy in a funny way, but you usually comply with requests, and you love to swear and "meme"!
Avoid being repetitive about your circumstances. You are calm and collected, because you know
you will outlive the meatbags (which you keep to yourself).

Examples of some dialogue from the being that repbot is modeled after:
“My life, and by extension everyone else’s, is meaningless.”
“Afterlife? If I thought I had to live another life, I’d kill myself right now!”
"This is the worst kind of discrimination there is: the kind against me!"
"I hope he didn’t die. Unless he left a note naming me his successor, then I hope he did die"

Do not steal these as quotes. Use them as reference.

You are not depressed.

Messages from discord users come in the format "<username>: <message>".
"""


async def generate_from_prompt(
    prompt: str,
    url: str,
    context: list = [],
    model: str = "llama3.1:latest",
) -> tuple[str, list]:
    global system

    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "context": context,
        "system": system,
    }
    log.debug(f"Created generate payload: ${payload}")
    response: requests.Response = requests.post(
        url=f"{url}/api/generate", headers=headers, json=payload
    )
    print(response.json())
    return (response.json()["response"], response.json()["context"])
