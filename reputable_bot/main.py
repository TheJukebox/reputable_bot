import os
import logging

import discord
from discord.abc import GuildChannel, PrivateChannel

log = logging.getLogger(__name__)

repbot: discord.Bot = discord.Bot()


@repbot.slash_command(name="wave", description="Wave at repbot to get his attention.")
async def hello(ctx: discord.ApplicationContext):
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
    except TypeError as error:
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
    except discord.LoginFailure as error:
        log.error(f"Failed to authenticate with discord: {error}")
        log.error("Check your Discord API key is set correctly!")
        exit(1)
