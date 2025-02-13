import os
import logging

from . import ollama

import discord
from discord.abc import GuildChannel, PrivateChannel

log = logging.getLogger(__name__)

repbot: discord.Bot = discord.Bot()

context: list = []


@repbot.slash_command(name="hey", description="Speak to repbot")
async def hey(ctx: discord.ApplicationContext, msg: str):
    log.debug(f"{ctx.author} used /hey")
    channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
    if channel:
        global context

        log.debug(f"{ctx.author}: {msg}")
        await ctx.response.defer()
        response = await ollama.generate_from_prompt(
            f"{ctx.author.display_name}: {msg}",
            "http://192.168.2.25:11434",
            context,
        )
        output: str = response[0]
        context = response[1]

        if len(output) < 2000:
            log.debug(f"Responding with: {output}")
            await ctx.send_followup(f"_{ctx.author.display_name} said, '{msg}'_\n\n{output}")
        else:
            chunks = [output[i : i + 2000] for i in range(0, len(output), 2000)]
            await ctx.send_followup(f"_{ctx.author.display_name} said, '{output}'_\n\n{chunks[0]}")
            log.debug(f"Responding with: {chunks[0]}")
            for chunk in chunks[1:]:
                log.debug(f"Responding with: {chunk}")
                await repbot.get_channel(ctx.channel_id).send(chunk)


@repbot.slash_command(name="wave", description="Wave at repbot to get his attention.")
async def wave(ctx: discord.ApplicationContext):
    log.debug(f"{ctx.author} used /wave.")
    channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
    if channel:
        await ctx.respond(f"Hey, {ctx.user.display_name}!")


@repbot.event
async def on_ready():
    log.info(f"Reputable Bot is online as {repbot.user}")
    try:
        default_channel = os.getenv("REPBOT_DEFAULT_CHANNEL_ID")
        default_channel = int(default_channel)
    except AttributeError as error:
        default_channel = None
        log.warning(
            f"REPBOT_DEFAULT_CHANNEL_ID set to an invalid value (must be int): {default_channel}"
        )
    except TypeError as error:
        default_channel = None
        log.warning(
            f"REPBOT_DEFAULT_CHANNEL_ID set to an invalid value (must be int): {default_channel}"
        )
    except NameError as error:
        default_channel = None
        log.warning(f"REPBOT_DEFAULT_CHANNEL_ID is not set!")

    if default_channel:
        await repbot.get_channel(default_channel).send("Hello, meatbags!")
    else:
        log.info("No default channel selected, just grabbing the first one we find...")
        channels = repbot.get_all_channels()
        # Send a message in the first text channel we can find
        for c in channels:
            if type(c) is discord.TextChannel:
                await repbot.get_channel(c.id).send("Hello, meatbags!")
                break


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        repbot.run(os.getenv("DISCORD_API_TOKEN"))
    except TypeError:
        log.error(
            f"Failed to authenticate with discord, DISCORD_API_TOKEN is unset or incorrect."
        )
        exit(1)
    except discord.LoginFailure as error:
        log.error(f"Failed to authenticate with discord: {error}")
        log.error("Check your Discord API key is set correctly!")
        exit(1)
