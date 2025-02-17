import random
import logging

from . import ollama
from . import env
from . import utils

import discord
from discord import default_permissions
from discord.abc import GuildChannel, PrivateChannel

log = logging.getLogger("repbot")

intents: discord.Intents = discord.Intents.default()
intents.typing = True
intents.messages = True
intents.message_content = True
repbot: discord.Bot = discord.Bot(intents=intents)

context: list = []

RESPONSIVE_BASE = 70
RESPONSIVE_DURATION_BASE = 5

channel_attention = 0
responsive_duration = RESPONSIVE_DURATION_BASE
responsive_ignore_channels = set()
responsive_ignore_user = set()


def random_channel() -> discord.TextChannel:
    id = random.choice(
        [
            channel
            for channel in repbot.get_all_channels()
            if type(channel) is discord.TextChannel
        ]
    ).id
    return repbot.get_channel(id)


@repbot.slash_command(
    name="ignore",
    description="Tells repbot to ignore you. You can get his attention with /wave",
)
async def ignore(ctx: discord.ApplicationCommand):
    responsive_ignore_user.add(ctx.author)
    log.info("Ignoring {ctx.author}.")
    await ctx.respond("I'll ignore you until you give me a wave.")


@repbot.slash_command(name="slap", description="Puts repbot in his place")
async def slap(ctx: discord.ApplicationCommand):
    if type(ctx.channel) is not discord.TextChannel:
        return
    else:
        log.debug(f"{ctx.author} used /slap")
        responsive_ignore_channels.add(ctx.channel)
        channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
        if channel:
            global context

            await ctx.response.defer()
            response = await ollama.generate_from_prompt(
                prompt=f"{ctx.author.display_name} slaps repbot in the face so he shuts the fuck up in #{ctx.channel.name}. They must have really hated something repbot said...\n Repbot:",
                url=env.REPBOT_OLLAMA_URL,
                context=context,
                model=env.REPBOT_DEFAULT_MODEL,
            )
            output: str = response[0]
            context = response[1]
            await ctx.respond(output)


@repbot.slash_command(
    name="train",
    description="Fetches (n) messages from the current channel and converts them to training data.",
)
@default_permissions(administrator=True)
async def train(ctx: discord.ApplicationCommand, n: int):
    if type(ctx.channel) is not discord.TextChannel:
        await ctx.respond("This isn't a text channel, ya numpty")
    else:
        await ctx.response.defer()
        log.info("Writing training data to file...")
        path = await utils.write_message_data(ctx.channel, n)
        log.info(f"Wrote training data to {path}!")
        await ctx.respond("mmm yum mmm yummy yum data mmmf")


@repbot.slash_command(name="hey", description="Speak to repbot")
async def hey(ctx: discord.ApplicationContext, msg: str):
    log.debug(f"{ctx.author} used /hey")
    channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
    if channel:
        global context

        log.debug(f"{ctx.author}: {msg}")
        await ctx.response.defer()
        response = await ollama.generate_from_prompt(
            prompt=f"{msg}",
            url=env.REPBOT_OLLAMA_URL,
            context=context,
            model=env.REPBOT_DEFAULT_MODEL,
        )
        output: str = response[0]
        context = response[1]

        # TODO: fix chunks
        if len(output) < 2000:
            log.debug(f"Responding with: {output}")
            await ctx.send_followup(
                f"_{ctx.author.display_name} said, '{msg}'_\n\n{output}"
            )
        else:
            chunks = [output[i : i + 2000] for i in range(0, len(output), 2000)]
            await ctx.send_followup(
                f"_{ctx.author.display_name} said, '{output}'_\n\n{chunks[0]}"
            )
            log.debug(f"Responding with: {chunks[0]}")
            for chunk in chunks[1:]:
                log.debug(f"Responding with: {chunk}")
                await repbot.get_channel(ctx.channel_id).send(chunk)


@repbot.slash_command(name="wave", description="Wave at repbot to get his attention.")
async def wave(ctx: discord.ApplicationContext):
    log.info(f"{ctx.author} waved at repbot. Resetting attention!")
    log.info(f"Now focusing on {ctx.channel.name} ({ctx.channel.id})")
    global channel_attention
    global responsive_duration
    channel_attention = ctx.channel
    responsive_duration = RESPONSIVE_DURATION_BASE

    channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
    if channel:
        global context

        await ctx.response.defer()
        log.info("Updating responsiveness ignore lists...")
        if ctx.channel in responsive_ignore_channels:
            responsive_ignore_channels.remove(ctx.channel)
        if ctx.author in responsive_ignore_user:
            responsive_ignore_user.remove(ctx.author)
        log.debug(responsive_ignore_channels)
        log.debug(responsive_ignore_user)
        response = await ollama.generate_from_prompt(
            prompt=f"{ctx.author.display_name} waves at repbot from the #{ctx.channel.name} channel to get his attention\nRepbot:",
            url=env.REPBOT_OLLAMA_URL,
            context=context,
            model=env.REPBOT_DEFAULT_MODEL,
        )
        output: str = response[0]
        context = response[1]
        await ctx.respond(output)


def should_respond(channel: discord.TextChannel) -> bool:
    global responsive_duration
    respond_chance = RESPONSIVE_BASE
    log.debug(f"Deciding if we should respond... base chance is {respond_chance}")
    if channel == channel_attention:
        log.debug("This channel is our current focus - increasing response chance.")
        respond_chance -= 5
    if responsive_duration > 0:
        log.debug("We're still feeling chatty - increasing response chance.")
        respond_chance -= 2 * responsive_duration
    if channel in responsive_ignore_channels:
        log.debug("We've been slapped here, we probably shouldn't chat...")
        respond_chance += 25
    log.debug(
        f"Randomly determining if we should respond with a ~{100 - respond_chance}% chance..."
    )
    if random.randint(1, 100) >= respond_chance:
        responsive_duration -= 1
        return True
    else:
        return False


@repbot.listen()
async def on_message(msg: discord.Message):
    global context

    if msg.author == repbot.user or msg.author in responsive_ignore_user:
        return

    if repbot.user in msg.mentions:
        log.info("Repbot was mentioned in a message.")
        log.info("Generating a response!")
        response = await ollama.generate_from_prompt(
            prompt=f"{msg.author.display_name}: {msg.content.replace(repbot.user.mention+" ", "")}\nRepbot:",
            url=env.REPBOT_OLLAMA_URL,
            context=context,
            model=env.REPBOT_DEFAULT_MODEL,
        )
        output: str = response[0]
        context = response[1]
        log.info(f"Responding with: '{output}'")
        await repbot.get_channel(msg.channel.id).send(output)
    elif should_respond(msg.channel):
        log.info("Responding to random message.")
        response = await ollama.generate_from_prompt(
            prompt=f"{msg.author.display_name}: \nRepbot:",
            url=env.REPBOT_OLLAMA_URL,
            context=context,
            model=env.REPBOT_DEFAULT_MODEL,
        )
        output: str = response[0]
        context = response[1]
        log.info(f"Sending message: '{output}'")
        await repbot.get_channel(msg.channel.id).send(output)
    else:
        log.debug("Not responding message.")


@repbot.event
async def on_ready():
    log.info(f"Reputable Bot is online as {repbot.user}")
    log.info(f"Default channel ID is {env.REPBOT_DEFAULT_CHANNEL_ID}")

    if not env.REPBOT_DEFAULT_CHANNEL_ID:
        log.warning("REPBOT_DEFAULT_CHANNEL_ID is not set.")
        channel: discord.TextChannel = random_channel()
    else:
        try:
            channel = repbot.get_channel(env.REPBOT_DEFAULT_CHANNEL_ID)
            log.info(f"Default channel set: {channel.name} ({channel.id})")
        except AttributeError:
            log.warning(
                f"REPBOT_DEFAULT_CHANNEL_ID is set to an invalid ID for this server: {env.REPBOT_DEFAULT_CHANNEL_ID}"
            )
            log.info(f"Available channels are: ")
            for c in repbot.get_all_channels():
                if type(c) is discord.TextChannel:
                    log.info(f"\t{c.name}: {c.id}")
            log.info(f"Selecting a random channel for now...")
            channel: discord.TextChannel = random_channel()

    await channel.send("Hey, meatbags!")
    log.info(
        f"Sent greeting message. Attention now focused on default channel: {channel.name}"
    )
    global channel_attention
    channel_attention = channel


if __name__ == "__main__":
    env.setup()
    logging.basicConfig(level=env.REPBOT_LOG_LEVEL)
    log.info("🤖 Environment initialised! 🤖")
    log.info(f"🗒️ Log level: {env.REPBOT_LOG_LEVEL}")
    log.info(f"📻 Default channel ID: {env.REPBOT_DEFAULT_CHANNEL_ID}")
    log.info(f"🦙 Ollama URL: {env.REPBOT_OLLAMA_URL}")
    log.info(f"👤 Default model: {env.REPBOT_DEFAULT_MODEL}")
    log.info(f"🧠 System message: {env.REPBOT_SYSTEM_MESSAGE}")
    log.info("Happy shitposting!")

    try:
        repbot.run(env.REPBOT_DISCORD_API_TOKEN)
    except discord.LoginFailure as error:
        log.error(f"Failed to authenticate with discord: {error}")
        log.error("Check your Discord API key is set correctly!")
        exit(1)
