import random
import logging
import asyncio
from pathlib import Path

from . import chat
from . import dungeon
from . import env
from . import ollama
from . import utils
from . import routines

import markovify
import discord
from discord import default_permissions

log = logging.getLogger("repbot")

intents: discord.Intents = discord.Intents.default()
intents.typing = True
intents.messages = True
intents.message_content = True
repbot: discord.Bot = discord.Bot(intents=intents)

context: list = []

RESPONSIVE_BASE = 85
RESPONSIVE_DURATION_BASE = 5

channel_attention = 0
responsive_duration = RESPONSIVE_DURATION_BASE
responsive_disliked_channels = set()
responsive_ignored_channels = set()
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


async def handle_message(prompt: str, update_context: bool = False) -> str:
    global context
    response = await ollama.generate_from_prompt(
        prompt=prompt,
        context=context,
        url=env.REPBOT_OLLAMA_URL,
        model=env.REPBOT_DEFAULT_MODEL,
        system=env.REPBOT_SYSTEM_MESSAGE,
    )

    if update_context:
        context = response[1]

    return response[0]


@repbot.slash_command(name="markov", description="Generate a markov chain from chat.")
async def markov(ctx: discord.ApplicationCommand):
    log.info("Creating markov chain...")
    await ctx.response.defer()
    log.info("Fetching messages...")
    if ctx.channel_id not in chat.message_cache.keys():
        chat.message_cache[ctx.channel_id] = [
            message["content"]
            async for message in utils.fetch_messages(ctx.channel, 5000)
        ]
    else:
        messages = chat.message_cache[ctx.channel_id]
    pool = "\n".join(messages)
    log.info("Generating text...")
    model = markovify.Text(pool)
    result = model.make_short_sentence(2000)
    log.info(f"Got result: {result}")
    await ctx.respond(result)


@repbot.slash_command(name="think", description="Make repbot think a powerful thought.")
async def think(ctx: discord.ApplicationCommand):
    # Create a markov model from cache
    log.info("Thinking about markov chain...")
    global context
    await ctx.response.defer()
    log.info("Fetching messages...")
    if ctx.channel_id not in chat.message_cache.keys():
        chat.message_cache[ctx.channel_id] = [
            message["content"]
            async for message in utils.fetch_messages(ctx.channel, 5000)
        ]
    else:
        messages = chat.message_cache[ctx.channel_id]
    pool = "\n".join(messages)

    # Generate a chain
    log.info("Generating text...")
    model = markovify.Text(pool)
    result = model.make_short_sentence(100)
    log.info(f"Got result: {result}")

    # Think about the chain with the LLM
    log.info("Thinking about it...")
    response: str = await handle_message(
        f"Repbot thinks: *{result}*\n\nreputablebot: ", True
    )
    log.info(f"Generated response: {response}")

    # Respond via the command context
    output: str = f"*Repbot thinks: '{result}'*\n\n{response}"
    log.info(f"Responding with: {output}")
    await ctx.respond(output)


@repbot.slash_command(
    name="ignore",
    description="Tells repbot to ignore you. You can get his attention with /wave",
)
async def ignore(ctx: discord.ApplicationCommand):
    responsive_ignore_user.add(ctx.author)
    log.info(f"Ignoring {ctx.author}.")
    await ctx.respond("I'll ignore you until you give me a wave.")


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


@repbot.slash_command(
    name="newdungeon",
    description="Resets reputable dungeon. WARNING: Repbot forgets EVERYTHING about the current round.",
)
async def new_dungeon(ctx: discord.ApplicationCommand):
    if ctx.channel.id != env.REPBOT_DUNGEON_CHANNEL_ID:
        await ctx.respond(
            f"This command only works in {repbot.get_channel(env.REPBOT_DUNGEON_CHANNEL_ID).jump_url}"
        )
    else:
        await ctx.respond("## 🔄 Resetting the table! 🔄")
        await dungeon.init_dungeon(repbot.get_channel(env.REPBOT_DUNGEON_CHANNEL_ID))


@repbot.slash_command(name="hey", description="Speak to repbot")
async def hey(ctx: discord.ApplicationContext, msg: str):
    log.debug(f"{ctx.author} used /hey")
    channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
    if channel:
        log.debug(f"{ctx.author}: {msg}")
        await ctx.response.defer()
        response: str = await handle_message(msg, True)
        await ctx.send_followup(
            f"_{ctx.author.display_name} said, '{msg}'_\n\n{response}"
        )


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
        if ctx.channel in responsive_disliked_channels:
            responsive_disliked_channels.remove(ctx.channel)
        if ctx.author in responsive_ignore_user:
            responsive_ignore_user.remove(ctx.author)
        log.debug(responsive_disliked_channels)
        log.debug(responsive_ignore_user)
        response: str = await handle_message(
            f"{ctx.author.display_name} waves at repbot from the #{ctx.channel.name} channel to get his attention\nreputablebot: ",
            True,
        )
        await ctx.respond(response)


@repbot.slash_command(name="slap", description="Puts repbot in his place")
async def slap(ctx: discord.ApplicationCommand):
    if type(ctx.channel) is not discord.TextChannel:
        return
    else:
        log.debug(f"{ctx.author} used /slap")
        responsive_disliked_channels.add(ctx.channel)
        channel = repbot.get_channel(ctx.channel_id) if ctx.channel_id else None
        if channel:
            await ctx.response.defer()
            response: str = await handle_message(
                f"{ctx.author.display_name} slaps reputablebot in the face so he shuts the fuck up in #{ctx.channel.name}. They must have really hated something repbot said...\nreputablebot: ",
                True,
            )
            await ctx.respond(response)


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
        responsive_duration -= 1
    if channel in responsive_disliked_channels:
        log.debug("We've been slapped here, we probably shouldn't chat...")
        respond_chance += 25
    log.debug(
        f"Randomly determining if we should respond with a ~{100 - respond_chance}% chance..."
    )
    chance = random.randint(1, 100)
    if chance >= respond_chance:
        log.debug(f"Got {chance}/{respond_chance} and decided to respond.")
        return True
    else:
        log.debug(f"Got {chance}/{respond_chance} and decided not to respond.")
        return False


@repbot.listen()
async def on_message(message: discord.Message):
    if (
        message.channel.id == env.REPBOT_DUNGEON_CHANNEL_ID
        and message.author != repbot.user
    ):
        if message.content[0] in ["#", "!", "/"]:
            return
        await dungeon.on_message(message)

    if message.author == repbot.user or message.author in responsive_ignore_user:
        return

    if message.channel in responsive_ignored_channels:
        return

    if repbot.user in message.mentions or should_respons(message.channel):
        log.info(f"Responding to message: {message.author}: '{message.content}'")
        async with message.channel.typing():
            await chat.respond(message)


@repbot.event
async def on_ready():
    log.info(f"Reputable Bot is online as {repbot.user}")
    log.info(f"Default channel ID is {env.REPBOT_DEFAULT_CHANNEL_ID}")

    log.info("Initialising chat...")
    text_channels: list[discord.TextChannel] = [channel for channel in repbot.get_all_channels() if type(channel) is discord.TextChannel]
    await chat.init(Path("context.json"), text_channels)

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

    log.info("Setting up reputable dungeon...")
    if not env.REPBOT_DUNGEON_CHANNEL_ID:
        log.warning("No dungeon channel set")
    else:
        log.info("doin it")
        dungeon_channel = repbot.get_channel(env.REPBOT_DUNGEON_CHANNEL_ID)
        responsive_ignored_channels.add(dungeon_channel)
        await dungeon.init_dungeon(dungeon_channel)


if __name__ == "__main__":
    env.setup()
    logging.basicConfig(level=env.REPBOT_LOG_LEVEL)
    log.info("🤖 Environment initialised! 🤖")
    log.info(f"🗒️ Log level: {env.REPBOT_LOG_LEVEL}")
    log.info(f"📻 Default channel ID: {env.REPBOT_DEFAULT_CHANNEL_ID}")
    log.info(f"🧙 Dungeon channel ID: {env.REPBOT_DUNGEON_CHANNEL_ID}")
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
