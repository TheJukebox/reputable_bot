# reputable\_bot
![lint](https://gitea.bogan.io/jukebox/reputable_bot/actions/workflows/lint.yaml/badge.svg)
![build](https://gitea.bogan.io/jukebox/reputable_bot/actions/workflows/build.yaml/badge.svg)

Reputable Bot is a Discord bot built with [Pycord](https://pycord.dev/), that leverages
[Ollama](https://ollama.com/) for generating completions.


## Requirements

You can install the project's Python requirements with `pip`:

```sh
pip install -r requirements
```

To generate completions, Reputablebot requires access to a working
[Ollama](https://ollama.com/) server. You can check 
[their documentation](https://github.com/ollama/ollama/blob/main/README.md)
for details!

## Usage

You can run Repbot directly in your terminal with the following commands:

```sh
pip install -e . && python -m reputable_bot
```

Or you can use a container:

```sh
docker build . -t repbot:local
docker run repbot:local
# You can also pull the latest build
docker run gitea.bogan.io/jukebox/repbot:latest
# Or a specific tag:
docker run gitea.bogan.io/jukebox/repbot:1.0.3
```

## Configuration

Repbot is configured using environment variables, to facilitate ease of configuration when
containerised.

| Variable | Description | Default |
|----------|-------------|---------|
| (string) (required) `REPBOT_DISCORD_API_TOKEN` | A Discord API token that allows authentication with Discord. | |
| (string) `REPBOT_OLLAMA_URL` | The URL of an Ollama server, used to generate responses. | `http://localhost:11343` |
| (string) `REPBOT_DEFAULT_MODEL` | The default model tag to use with Ollama. | `llama3.1:latest` |
| (string) `REPBOT_CONTEXT_WINDOW` | Sets the number of tokens in the context window. | `2048` |
| (string) `REPBOT_DEFAULT_CHANNEL_ID` | The ID of a channel in Discord that Repbot announces its presence in and focuses its attention on to start. | Randomly chosen from available text channels. |
| (string) `REPBOT_DUNGEON_CHANNEL_ID` | The ID of a channel in Discord that Repbot will use to run Reputable Dungeon. |  Reputable Dungeon is disable if not set.  |
| (string) `REPBOT_LOG_LEVEL` | Sets the log level. `info`, `debug`, and `error` are the possible options. | `info` |

