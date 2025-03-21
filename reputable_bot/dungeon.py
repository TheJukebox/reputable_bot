import random

from . import env
from . import ollama
from . import logging


import markovify
from discord import TextChannel
from discord import Message

log = logging.setup_log(__name__)
log.setLevel(env.REPBOT_LOG_LEVEL)

context: list[int] = []
system: str

readme: str = r"""
```
        ,  ,  _,,    _, _,  , ,  _,    ___,_,. 
        | ,| /_,|   /  / \,|\/| /_,   ' | / \, 
        |/\|'\_'|__'\_'\_/ | `|'\_      |'\_/  
        '  `   `  '   `'   '  `   `     ' ' 
█▄▄▄▄ ▄███▄   █ ▄▄   ▄     ▄▄▄▄▀ ██   ███   █     ▄███▄   
█  ▄▀ █▀   ▀  █   █   █ ▀▀▀ █    █ █  █  █  █     █▀   ▀  
█▀▀▌  ██▄▄    █▀▀▀ █   █    █    █▄▄█ █ ▀ ▄ █     ██▄▄    
█  █  █▄   ▄▀ █    █   █   █     █  █ █  ▄▀ ███▄  █▄   ▄▀ 
  █   ▀███▀    █   █▄ ▄█  ▀         █ ███       ▀ ▀███▀   
 ▀              ▀   ▀▀▀            █                      
                                  ▀                       
    ██▄     ▄      ▄     ▄▀  ▄███▄   ████▄    ▄           
    █  █     █      █  ▄▀    █▀   ▀  █   █     █          
    █   █ █   █ ██   █ █ ▀▄  ██▄▄    █   █ ██   █         
    █  █  █   █ █ █  █ █   █ █▄   ▄▀ ▀████ █ █  █         
    ███▀  █▄ ▄█ █  █ █  ███  ▀███▀         █  █ █         
           ▀▀▀  █   ██                     █   ██   
```
## 📜 How to Play 📜
Shortly I'll introduce the world and we can begin. All you need to do is send a message in this chat and I'll respond! Be warned, the rules are very loose and my brain is very, very smooth.

I'll generate some random info about the game, like the ruleset name, the genre, and I'll think really hard about the world. This should influence the rest of the game, but don't get mad if I'm terrible at staying on track.

## 🚫 Ignoring Messages 🚫
I will ignore messages that start with '#', '!', or '/' so you can talk without me butting in. Otherwise, I respond to everything said in this chat, so try not to speak over each other if you don't want me to smooth my brain.

## 🔄 Resetting 🔄
You can use `/newdungeon` in this channel to reset the game. This wipes everything, so be careful about it! 
"""


async def init_dungeon(channel: TextChannel):
    global system
    global context

    rule_systems: list[str] = [
        "BX D&D",
        "D&D 5e",
        "D20 Skill Based",
        "D100 Skill Based",
        "D6 Pool Based",
        "OSR",
    ]
    # with open("sources/systems.txt", "r") as f:
    #     stems: list[str] = f.readlines()
    #     rule_system: str = random.choice(stems).strip("\n")
    #     rule_system += f" {random.choice(stems).strip("\n")}"
    with open("sources/genres.txt", "r") as f:
        stems: list[str] = f.readlines()
        genre: str = random.choice(stems).strip("\n")
        genre += f" {random.choice(stems).strip("\n")}"
    with open("sources/worlds.txt", "r") as f:
        model: markovify.Text = markovify.Text(f.read())
        world_description: str | None = model.make_short_sentence(100)
        log.info(f"World description generated: {world_description}")

    system = (
        f"You are reputablebot, an amoral, gonzo AI gamemaster that impartially referees "
        + "a TTRPG in a discord channel. Never decide what player characters do or say on their behalf. "
        + "Sometimes the players will neeed to ask the GM (gamemaster) questions directly, these should be answered out of character. "
        + "You can use markdown formatting and emojis. "
        + "Below is information about the current TTRPG session:\n"
        + f"Rule System: {random.choice(rule_systems)}\n"
        + f"Genre: {genre}\n"
        + f"Description: {world_description}\n"
    )

    log.info(f"Sending dungeon readme to {channel.name}")
    await channel.send(readme)

    log.info(f"Sending generated prompts to {channel.name}")
    await channel.send(
        f"## The Setting\n"
        + f"I've generated some information about the game!\n"
        + f"### 📖 Genre: `{genre}`\n"
        + f"### 🍄 Inciting Hallucination: `{world_description}`"
    )

    async with channel.typing():
        log.info(f"Generating intro message")
        for i in range(4):
            response = await ollama.generate_from_prompt(
                prompt=f"Introduce the world, a starting location, and prompt the players to create their characters.",
                url=env.REPBOT_OLLAMA_URL,
                context=context,
                model=env.REPBOT_DEFAULT_MODEL,
                system=system,
            )
            if len(response[0]) > 2000:
                log.warning(f"Failed to produce a short enough output. Retrying [{i+1}/4]")
                continue
            output: str = response[0]
            context = response[1]
            log.info(f"Responding with: '{output}'")
            await channel.send("\n" + output)
            return
        log.error("We failed to generate a message <2000 characters long.")
        await channel.send(
            "even after 4 retries, i couldnt make a proper response. man do i suck. try prompting me again."
        )


async def on_message(msg: Message):
    global context
    log.info(f"Received message from {msg.author.display_name}: {msg.content}")
    chance: int = random.randint(0, 100)
    hints: list[str] = [
        "Foreshadow a combat encounter",
        "Foreshadow a trap",
        "Foreshadow an NPC",
        "Foreshadow a complication",
        "Foreshadow a new plot hook",
        "Introduce a combat encounter",
        "Introduce a trap",
        "Introduce an NPC",
        "Introduce a complication",
        "Introduce a new plot hook",
        "Reinforce the themes of the world",
        "Ambush!",
    ]
    if chance > 75:
        hint = random.choice(hints)
    else:
        hint: str = "Continue as normal"
    log.info(f"Prompting with hint: '{hint}'")

    for i in range(4):
        response = await ollama.generate_from_prompt(
            prompt=f"{msg.author.display_name}: {msg.content}\n<hint:{hint}>\nreputablebot: ",
            url=env.REPBOT_OLLAMA_URL,
            context=context,
            model=env.REPBOT_DEFAULT_MODEL,
            system=system,
        )
        if len(response[0]) > 2000:
            log.warning(f"Failed to produce a short enough output. Retrying [{i+1}/4]")
            continue
        output: str = response[0]
        context = response[1]
        log.info(f"Responding with: '{output}'")
        await msg.channel.send("\n" + output)
        return
    log.error("We failed to generate a message <2000 characters long.")
    await msg.channel.send(
        "even after 4 retries, i couldnt make a proper response. man do i suck. try prompting me again."
    )
